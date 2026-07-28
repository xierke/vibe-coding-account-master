"""
账单模块 Schema — 创建、编辑、查询、响应。
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


# ============================================================
# 创建账单
# ============================================================
class BillCreateRequest(BaseModel):
    """创建账单请求"""
    type: str                       # "income" 或 "expense"
    amount: float                  # 金额
    category_id: int               # 分类 ID
    bill_date: date | None = None  # 账单日期，默认当天
    note: str | None = None        # 备注，最多 200 字

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("income", "expense"):
            raise ValueError("类型必须为 income 或 expense")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0 or v > 999999999.99:
            raise ValueError("金额需在 0.01 ~ 999,999,999.99 之间")
        return round(v, 2)

    @field_validator("note")
    @classmethod
    def validate_note(cls, v: str | None) -> str | None:
        if v and len(v) > 200:
            raise ValueError("备注最多 200 字")
        return v


# ============================================================
# 编辑账单
# ============================================================
class BillUpdateRequest(BaseModel):
    """编辑账单请求 — 所有字段可选"""
    type: str | None = None
    amount: float | None = None
    category_id: int | None = None
    bill_date: date | None = None
    note: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str | None) -> str | None:
        if v is not None and v not in ("income", "expense"):
            raise ValueError("类型必须为 income 或 expense")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float | None) -> float | None:
        if v is not None:
            if v <= 0 or v > 999999999.99:
                raise ValueError("金额需在 0.01 ~ 999,999,999.99 之间")
            return round(v, 2)
        return v

    @field_validator("note")
    @classmethod
    def validate_note(cls, v: str | None) -> str | None:
        if v and len(v) > 200:
            raise ValueError("备注最多 200 字")
        return v


# ============================================================
# 批量删除
# ============================================================
class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: list[int]


# ============================================================
# 账单响应
# ============================================================
class CategoryBrief(BaseModel):
    """账单中内嵌的分类简要信息"""
    id: int
    name: str
    icon: str
    color: str

    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    """单条账单响应"""
    id: int
    type: str
    amount: float
    category: CategoryBrief | None = None
    bill_date: str         # "YYYY-MM-DD"
    note: str | None = None
    created_at: str        # ISO datetime string
    updated_at: str        # ISO datetime string

    class Config:
        from_attributes = True


class BillListResponse(BaseModel):
    """账单列表响应"""
    items: list[BillResponse]
    total: int
    page: int
    page_size: int
