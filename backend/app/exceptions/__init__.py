"""
自定义异常类 — 7 大 Iron Rules 之"每个错误都是类型化的"。
继承自 AppError，统一 code + status_code + message 格式。
"""


class AppError(Exception):
    """应用层异常基类。所有业务异常应继承此类。"""

    def __init__(self, message: str, code: int = 50000, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


# --- 400 系列 — 客户端错误 ---

class ValidationError(AppError):
    """参数校验失败 (40001)"""
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(message, code=40001, status_code=422)


class AuthError(AppError):
    """认证失败 — Token 过期/无效 (40100/40101)"""
    def __init__(self, message: str = "认证失败", code: int = 40101):
        super().__init__(message, code=code, status_code=401)


class ForbiddenError(AppError):
    """无权限访问 (40300)"""
    def __init__(self, message: str = "无权限访问"):
        super().__init__(message, code=40300, status_code=403)


class NotFoundError(AppError):
    """资源不存在 (40400)"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, code=40400, status_code=404)


class ConflictError(AppError):
    """资源冲突 — 如用户名已存在 (40900)"""
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, code=40900, status_code=409)


class RateLimitError(AppError):
    """请求过于频繁 (42900)"""
    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(message, code=42900, status_code=429)


class BusinessError(AppError):
    """通用业务逻辑错误 (50000)"""
    def __init__(self, message: str, code: int = 50000):
        super().__init__(message, code=code, status_code=400)
