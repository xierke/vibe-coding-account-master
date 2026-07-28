"""
Redis 连接管理。
使用 redis-py 异步客户端，提供连接获取/关闭与常用缓存操作。
所有缓存操作在 Redis 不可用时优雅降级（不抛出异常）。
"""
import logging
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("dailytracker.redis")

# 全局 Redis 连接池 (模块加载时不连接，首次使用时自动连接)
_redis_pool: aioredis.Redis | None = None
_redis_available: bool = True  # 标记 Redis 是否可用


async def is_redis_available() -> bool:
    """检查 Redis 是否可用。"""
    global _redis_available
    if not _redis_available:
        return False
    try:
        r = await get_redis()
        await r.ping()
        return True
    except Exception:
        _redis_available = False
        return False


async def get_redis() -> aioredis.Redis:
    """
    获取 Redis 连接。
    使用连接池模式，全局复用同一连接。
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            decode_responses=settings.redis_decode_responses,
            max_connections=20,
            socket_connect_timeout=2,     # 快速失败
            socket_timeout=2,
        )
    return _redis_pool


async def close_redis():
    """关闭 Redis 连接池，在应用 shutdown 时调用。"""
    global _redis_pool
    if _redis_pool is not None:
        try:
            await _redis_pool.aclose()
        except Exception:
            pass
        _redis_pool = None


# --- 缓存辅助工具函数 — 全部内置降级处理 ---

async def cache_get(key: str) -> str | None:
    """读取缓存，key 不存在或 Redis 不可用返回 None。"""
    global _redis_available
    if not _redis_available:
        return None
    try:
        r = await get_redis()
        return await r.get(key)
    except Exception:
        _redis_available = False
        logger.debug("Redis cache_get failed, disabling redis")
        return None


async def cache_set(key: str, value: str, ttl_seconds: int = 300):
    """写入缓存，带 TTL。Redis 不可用时静默跳过。"""
    global _redis_available
    if not _redis_available:
        return
    try:
        r = await get_redis()
        await r.set(key, value, ex=ttl_seconds)
    except Exception:
        _redis_available = False
        logger.debug("Redis cache_set failed, disabling redis")


async def cache_delete(key: str):
    """删除缓存 key。Redis 不可用时静默跳过。"""
    global _redis_available
    if not _redis_available:
        return
    try:
        r = await get_redis()
        await r.delete(key)
    except Exception:
        _redis_available = False
        logger.debug("Redis cache_delete failed, disabling redis")


async def cache_delete_pattern(pattern: str):
    """按模式删除缓存 key（如 `home:*`）。"""
    global _redis_available
    if not _redis_available:
        return
    try:
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
    except Exception:
        _redis_available = False
        logger.debug("Redis cache_delete_pattern failed, disabling redis")
