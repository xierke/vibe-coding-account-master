"""
数据库引擎与 Session 管理。
使用 SQLAlchemy 2.0 async engine + async_session_factory。
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# 异步引擎 — MySQL 通过 aiomysql 驱动
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,
    pool_pre_ping=True,  # 连接前检测有效性
)

# 异步 Session 工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不使对象过期，避免懒加载报错
)


async def get_db() -> AsyncSession:
    """
    FastAPI 依赖: 获取数据库 session。
    请求结束时自动关闭 session 归还连接池。
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
