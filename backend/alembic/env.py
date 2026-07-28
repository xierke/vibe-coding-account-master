"""
Alembic 环境配置 — 迁移脚本生成与执行。
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models import Base

# 导入所有模型，确保 Base.metadata 完整
from app.models.user import User
from app.models.category import Category
from app.models.bill import Bill
from app.models.budget import Budget

# Alembic Config 对象
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata 必须包含所有表
target_metadata = Base.metadata


def run_migrations_offline():
    """离线迁移 — 生成 SQL 脚本不执行。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """在线迁移 — 执行迁移。"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """异步迁移入口。"""
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    """在线迁移 — 使用异步引擎。"""
    asyncio.run(run_async_migrations())


# 根据模式选择离线或在线迁移
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
