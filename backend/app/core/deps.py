"""
FastAPI 依赖注入 — get_db, get_current_user, 限流依赖等。
"""
import uuid
from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import get_user_id_from_token
from app.exceptions import AuthError, RateLimitError

# Bearer Token 解析方案
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前登录用户。
    从 Authorization: Bearer <token> 中提取 user_id，查询数据库返回 User ORM 对象。
    未登录返回 AuthError(40101)。
    """
    if credentials is None:
        raise AuthError("请先登录", code=40101)

    try:
        user_id = get_user_id_from_token(credentials.credentials)
    except Exception:
        raise AuthError("Token 无效或已过期", code=40101)

    # 延迟导入避免循环依赖
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthError("用户不存在", code=40101)

    return user


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    """
    仅获取当前用户 ID（不查数据库）。
    适用于只需 user_id 做数据隔离，不需要完整 User 对象的场景。
    """
    if credentials is None:
        raise AuthError("请先登录", code=40101)

    try:
        return get_user_id_from_token(credentials.credentials)
    except Exception:
        raise AuthError("Token 无效或已过期", code=40101)


async def rate_limit(
    request: Request,
    limit_per_minute: int = 100,
):
    """
    基于用户或 IP 的速率限制（Redis 滑动窗口）。
    默认 100 次/分钟。
    """
    # 识别 key：优先用用户 ID，否则用 IP
    user_id = None
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            user_id = get_user_id_from_token(token)
    except Exception:
        pass

    client_key = f"user:{user_id}" if user_id else f"ip:{request.client.host}"
    redis_key = f"rate_limit:{client_key}"

    r = await get_redis()
    current = await r.get(redis_key)

    if current is None:
        # 首次请求，设置计数器并 60 秒过期
        await r.set(redis_key, 1, ex=60)
    elif int(current) >= limit_per_minute:
        raise RateLimitError("请求过于频繁，请稍后再试")
    else:
        await r.incr(redis_key)
