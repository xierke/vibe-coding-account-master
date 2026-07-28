"""
全局异常处理器 — 捕获所有 AppError 及未预期异常，统一返回格式。
"""
import traceback
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError

logger = logging.getLogger("dailytracker")


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器到 FastAPI 应用。"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        """处理所有 AppError 及其子类。"""
        logger.warning(
            "AppError",
            extra={
                "err_code": exc.code,
                "err_message": exc.message,
                "err_status": exc.status_code,
                "req_path": request.url.path,
                "req_id": getattr(request.state, "request_id", "N/A"),
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: requests.Request, exc: Exception):
        """处理未预期的异常 — 记录完整堆栈，返回通用 500。"""
        logger.error(
            "Unhandled exception",
            extra={
                "req_path": request.url.path,
                "req_id": getattr(request.state, "request_id", "N/A"),
                "err_detail": str(exc),
                "err_tb": traceback.format_exc(),
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "code": 50000,
                "message": "服务器内部错误",
                "detail": str(exc) if app.debug else "请稍后再试",
            },
        )
