"""
安全模块 — JWT Token 生成/验证 + bcrypt 密码哈希。
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from app.core.config import settings


# ============================================================
# 密码哈希 — bcrypt
# ============================================================

def hash_password(password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希。
    返回可直接存入数据库的哈希字符串。
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码与哈希是否匹配。
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ============================================================
# JWT Token — access_token + refresh_token
# ============================================================

def create_access_token(user_id: int) -> str:
    """
    生成短效 access_token (默认 15 分钟)。
    payload 仅包含 user_id，最小化 claims。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    """
    生成长效 refresh_token (默认 7 天)。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """
    解码并验证 JWT Token。
    无效/过期 Token 会抛出 jwt.PyJWTError。
    """
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )


def get_user_id_from_token(token: str) -> int:
    """从有效 Token 中提取 user_id。"""
    payload = decode_token(token)
    return int(payload["sub"])
