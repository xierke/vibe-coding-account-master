"""
DailyTracker — FastAPI 应用入口。
中间件注册、路由挂载、启动/关闭事件。
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, async_session_factory
from app.core.redis import close_redis
from app.exceptions.handlers import register_exception_handlers
from app.middleware import RequestIDMiddleware, LoggingMiddleware
from app.api import (
    auth_router,
    bills_router,
    categories_router,
    reports_router,
    budgets_router,
    users_router,
)


# ============================================================
# 日志配置
# ============================================================
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("dailytracker")


# ============================================================
# 生命周期事件
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用启动/关闭事件。
    启动：初始化默认分类数据，验证 DB/Redis 连接。
    关闭：释放连接池。
    """
    logger.info(f"=== {settings.app_name} v{settings.app_version} 启动中 ===")

    # 启动时确保默认分类数据存在
    try:
        from app.services.category_service import CategoryService
        async with async_session_factory() as db:
            await CategoryService.ensure_default_categories(db)
        logger.info("默认分类数据检查完成")
    except Exception as e:
        logger.warning(f"默认分类初始化失败 (DB 可能未就绪): {e}")

    logger.info(f"API 文档: http://localhost:8000/docs")
    logger.info(f"API 前缀: {settings.api_v1_prefix}")

    yield

    # 关闭
    logger.info("=== 应用关闭中 ===")
    try:
        await close_redis()
    except Exception:
        pass
    try:
        await engine.dispose()
    except Exception:
        pass
    logger.info("=== 应用已关闭 ===")


# ============================================================
# FastAPI 实例
# ============================================================
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="日常记账助手 — 轻量级个人收支管理 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================
# 中间件注册 (顺序重要)
# ============================================================
# 1. 请求 ID — 最外层，每个请求分配唯一 ID
app.add_middleware(RequestIDMiddleware)

# 2. 访问日志
app.add_middleware(LoggingMiddleware)

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 全局异常处理器
# ============================================================
register_exception_handlers(app)

# ============================================================
# 路由注册 — 统一挂载在 /v1 前缀下
# ============================================================
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(bills_router, prefix=settings.api_v1_prefix)
app.include_router(categories_router, prefix=settings.api_v1_prefix)
app.include_router(reports_router, prefix=settings.api_v1_prefix)
app.include_router(budgets_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)


# ============================================================
# 健康检查 — 无前缀，K8s / 负载均衡器使用
# ============================================================
@app.get("/health", tags=["系统"])
async def health_check():
    """Liveness probe — 应用是否存活。"""
    return {"status": "ok"}


@app.get("/ready", tags=["系统"])
async def readiness_check():
    """Readiness probe — 应用是否就绪 (DB + Redis 可用)。"""
    checks = {"database": "ok", "redis": "ok"}
    status_code = 200

    # 检查数据库
    try:
        from sqlalchemy import text
        async with async_session_factory() as db:
            await db.execute(text("SELECT 1"))
    except Exception as e:
        checks["database"] = str(e)
        status_code = 503

    # 检查 Redis
    try:
        from app.core.redis import get_redis
        r = await get_redis()
        await r.ping()
    except Exception as e:
        checks["redis"] = str(e)
        status_code = 503

    return {"status": "ok" if status_code == 200 else "degraded", "checks": checks}


# ============================================================
# 根路径
# ============================================================
@app.get("/", tags=["系统"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
