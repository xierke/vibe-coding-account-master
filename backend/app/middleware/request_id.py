"""
请求 ID 中间件 — 每个请求注入唯一 X-Request-ID。
日志和错误响应中使用，方便追踪链路。
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求生成/传递 X-Request-ID。"""

    async def dispatch(self, request: Request, call_next):
        # 优先复用上游传入的 Request-ID，否则生成新的
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id

        response = await call_next(request)

        # 写入响应头，方便前端排查
        response.headers["X-Request-ID"] = request_id
        return response
