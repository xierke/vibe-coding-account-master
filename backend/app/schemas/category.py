"""
分类模块 Schema — 创建、编辑、查询、响应。
"""
from datetime import datetime

from pydantic import BaseModel, field_validator


# ============================================================
# 创建分类
# ============================================================
class CategoryCreateRequest(BaseModel):
    """创建自定义分类请求"""
    name: str              # 分类名称
    icon: str              # 图标 (emoji)
    color: str             # 颜色 #RRGGBB
    type: str              # "income" 或 "expense"
    sort_order: int = 0    # 排序

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("分类名称不能为空")
        if len(v) > 30:
            raise ValueError("分类名称最多 30 个字符")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("income", "expense"):
            raise ValueError("类型必须为 income 或 expense")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("颜色格式必须为 #RRGGBB")
        return v


# ============================================================
# 编辑分类
# ============================================================
class CategoryUpdateRequest(BaseModel):
    """编辑分类请求 — 所有字段可选"""
    name: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("分类名称不能为空")
            if len(v) > 30:
                raise ValueError("分类名称最多 30 个字符")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if v is not None and (not v.startswith("#") or len(v) != 7):
            raise ValueError("颜色格式必须为 #RRGGBB")
        return v


# ============================================================
# 分类响应
# ============================================================
class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    name: str
    icon: str
    color: str
    type: str
    is_default: bool
    sort_order: int
    bill_count: int = 0        # 该分类下的账单数量（列表查询时填充）

    class Config:
        from_attributes = True
