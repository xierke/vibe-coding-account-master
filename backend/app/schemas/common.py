"""
统一 API 响应 Schema。
所有 API 返回的 JSON 格式：
  成功: { "code": 0, "message": "success", "data": {...} }
  分页: { "code": 0, "message": "success", "data": { "items": [...], "total": ..., "page": ..., "page_size": ... } }
  错误: { "code": ..., "message": "...", "detail": "..." }
"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """通用成功响应"""
    code: int = 0
    message: str = "success"
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    """分页数据结构"""
    items: list[T]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    """错误响应结构"""
    code: int
    message: str
    detail: str | None = None
