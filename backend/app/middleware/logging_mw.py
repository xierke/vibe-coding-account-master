"""
结构化访问日志中间件 — 记录每个请求的方法、路径、耗时、状态码。
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("dailytracker.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """记录请求日志（结构化 JSON 格式）。"""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "req_method": request.method,
                "req_path": request.url.path,
                "resp_status": response.status_code,
                "resp_duration_ms": duration_ms,
                "req_id": getattr(request.state, "request_id", "N/A"),
                "client_ip": request.client.host if request.client else "N/A",
            },
        )
        return response
