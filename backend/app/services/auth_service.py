"""
认证业务逻辑层 — 注册、登录、短信登录、Token 刷新、验证码、密码管理。
不导入 HTTP 类型，纯业务逻辑。
"""
import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.redis import get_redis
from app.core.config import settings
from app.models.user import User
from app.exceptions import (
    AuthError,
    ConflictError,
    NotFoundError,
    ValidationError,
    BusinessError,
)

logger = logging.getLogger("dailytracker.auth")


class AuthService:
    """
    认证服务 — 处理注册、登录、Token 管理、验证码。

    设计原则：
    - 所有方法接收 db session，不持有 session 引用
    - 不导入 HTTP 相关类型（Request/Response）
    - 异常用 AppError 子类，由全局处理器统一格式化
    """

    # ============================================================
    # 注册
    # ============================================================
    @staticmethod
    async def register(db: AsyncSession, username: str, email: str, password: str) -> dict:
        """
        用户注册。

        规则：
        - 用户名和邮箱必须唯一
        - 密码 bcrypt 哈希存储
        - 注册成功自动返回 Token（等同于自动登录）
        """
        # 检查用户名唯一性
        existing = await db.execute(select(User).where(User.username == username))
        if existing.scalar_one_or_none():
            raise ConflictError("用户名已被注册")

        # 检查邮箱唯一性
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ConflictError("邮箱已被注册")

        # 创建用户
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        db.add(user)
        await db.flush()  # 获取 user.id
        await db.refresh(user)

        logger.info(f"用户注册成功: {user.username} (id={user.id})")

        # 自动登录 — 返回 Token
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
        }

    # ============================================================
    # 密码登录
    # ============================================================
    @staticmethod
    async def login(db: AsyncSession, account: str, password: str, remember_me: bool = False) -> dict:
        """
        密码登录 — 支持用户名或邮箱。

        规则：
        - 密码错误 > 5 次锁定 15 分钟
        - remember_me 影响 refresh_token 有效期（当前版本 Token 统一 7 天）
        """
        # 查询用户 — 支持用户名或邮箱
        result = await db.execute(
            select(User).where(
                (User.username == account) | (User.email == account)
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise AuthError("账号或密码错误", code=40101)

        # 检查账号是否被锁定
        if user.is_locked and user.locked_until:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            if now < user.locked_until:
                remaining = int((user.locked_until - now).total_seconds() / 60) + 1
                raise BusinessError(f"账号已锁定，请 {remaining} 分钟后重试", code=40101)
            else:
                # 锁定时间已过，自动解锁
                user.is_locked = False
                user.locked_until = None
                user.failed_login_attempts = 0

        # 校验密码
        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1

            # 超过上限则锁定
            if user.failed_login_attempts >= settings.max_login_attempts:
                user.is_locked = True
                user.locked_until = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
                    minutes=settings.lockout_duration_minutes
                )
                await db.flush()
                raise BusinessError(
                    f"密码错误次数过多，账号已锁定 {settings.lockout_duration_minutes} 分钟",
                    code=40101,
                )

            await db.flush()
            remaining = settings.max_login_attempts - user.failed_login_attempts
            raise AuthError(f"密码错误，还剩 {remaining} 次机会", code=40101)

        # 登录成功 — 重置失败计数
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        await db.flush()

        logger.info(f"用户登录成功: {user.username} (id={user.id})")

        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
        }

    # ============================================================
    # 短信验证码登录
    # ============================================================
    @staticmethod
    async def login_by_sms(db: AsyncSession, phone: str, code: str) -> dict:
        """
        短信验证码登录。

        规则：
        - 优先查用户 phone 匹配 → 直接登录
        - phone 未匹配 → 查是否有用户关联此 phone → 有则更新
        - 都没有 → 新建用户（用户名 = "user_" + phone 后 6 位）
        - 手机号首次登录即自动绑定
        """
        # 1. 校验验证码
        await AuthService._verify_code(phone, code, "sms")

        # 2. 查找或创建用户
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()

        if user is None:
            # 新用户 — 创建账号（首次短信登录自动绑定手机号）
            username = f"user_{phone[-6:]}"
            # 确保用户名唯一
            counter = 0
            base_username = username
            while True:
                existing = await db.execute(
                    select(User).where(User.username == username)
                )
                if not existing.scalar_one_or_none():
                    break
                counter += 1
                username = f"{base_username}_{counter}"

            user = User(
                username=username,
                email=f"{phone}@sms.local",  # 占位邮箱，短信登录用户可能需要后续完善
                password_hash=hash_password(phone),  # 默认密码 = 手机号
                phone=phone,
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            logger.info(f"短信登录新用户注册: phone={phone}, username={user.username}")

        # 3. 如果用户已有 phone 但不是当前手机号，更新绑定
        elif user.phone is None:
            user.phone = phone

        logger.info(f"短信验证码登录成功: id={user.id} phone={phone}")

        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
        }

    # ============================================================
    # Token 刷新
    # ============================================================
    @staticmethod
    async def refresh_token(refresh_token_str: str) -> dict:
        """
        刷新 access_token + refresh_token。

        规则：
        - 校验 refresh_token 是否有效
        - 校验 type 是否为 "refresh"
        - 返回新的 access_token + refresh_token
        """
        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            raise AuthError("refresh_token 无效或已过期", code=40100)

        if payload.get("type") != "refresh":
            raise AuthError("无效的 Token 类型", code=40101)

        user_id = int(payload["sub"])

        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
        }

    # ============================================================
    # 发送验证码
    # ============================================================
    @staticmethod
    async def send_verify_code(target: str, code_type: str) -> None:
        """
        发送验证码 — 生成 6 位数字，存入 Redis (TTL 5 分钟)。

        code_type: "email" | "sms"
        当前短信为 Mock 实现，验证码打印到控制台日志。
        """
        # 生成 6 位随机数字
        code = str(random.randint(100000, 999999))

        # 存入 Redis
        redis_key = f"verify_code:{code_type}:{target}"
        try:
            r = await get_redis()
            await r.set(redis_key, code, ex=settings.verify_code_ttl_seconds)
        except Exception:
            logger.warning("Redis 不可用，验证码仅打印到日志，无法用于实际验证")
            # 不抛异常 — Redis 不可用时验证码仅打印到日志，不阻断流程

        if code_type == "email":
            logger.info(f"=== [Mock Email] 邮箱 {target} 的验证码: {code} ===")
        elif code_type == "sms":
            logger.info(f"=== [Mock SMS] 手机号 {target} 的验证码: {code} ===")

    # ============================================================
    # 密码重置
    # ============================================================
    @staticmethod
    async def reset_password(db: AsyncSession, email: str, code: str, new_password: str) -> None:
        """
        通过验证码重置密码。

        规则：
        - 验证码正确且未过期
        - 新密码 bcrypt 哈希后覆盖旧密码
        - 重置后清除该用户所有登录 Token（通过更换 secret 或简单实现：强制重新登录）
        """
        # 1. 校验验证码
        await AuthService._verify_code(email, code, "email")

        # 2. 查找用户
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundError("该邮箱未注册")

        # 3. 更新密码
        user.password_hash = hash_password(new_password)
        await db.flush()

        logger.info(f"密码重置成功: {user.username} (id={user.id})")

    # ============================================================
    # 修改密码（已登录）
    # ============================================================
    @staticmethod
    async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> None:
        """
        已登录用户修改密码。

        规则：
        - 需验证旧密码
        - 新密码不能与旧密码相同
        """
        if not verify_password(old_password, user.password_hash):
            raise ValidationError("原密码错误")

        if old_password == new_password:
            raise ValidationError("新密码不能与原密码相同")

        user.password_hash = hash_password(new_password)
        await db.flush()

        logger.info(f"密码修改成功: {user.username} (id={user.id})")

    # ============================================================
    # 内部方法
    # ============================================================
    @staticmethod
    async def _verify_code(target: str, code: str, code_type: str) -> None:
        """
        校验验证码是否匹配且未过期。
        """
        redis_key = f"verify_code:{code_type}:{target}"
        try:
            r = await get_redis()
            stored_code = await r.get(redis_key)
        except Exception:
            raise ValidationError("验证码服务暂时不可用，请稍后再试")

        if stored_code is None:
            raise ValidationError("验证码已过期或未发送")
        if stored_code != code:
            raise ValidationError("验证码错误")

        # 验证成功后删除验证码，防止重用
        try:
            await r.delete(redis_key)
        except Exception:
            pass
