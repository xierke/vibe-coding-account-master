"""
预算模块 Schema — 设置/获取预算。
"""
from pydantic import BaseModel, field_validator


# ============================================================
# 预算条目
# ============================================================
class BudgetItem(BaseModel):
    """单条预算"""
    category_id: int | None = None  # None = 总预算
    category_name: str | None = None
    amount: float
    spent: float = 0.0              # 已花费金额
    usage_rate: float = 0.0         # 使用率 0.0 ~ 1.0


# ============================================================
# 设置预算
# ============================================================
class BudgetSetRequest(BaseModel):
    """设置/更新预算请求"""
    month: str                       # "YYYY-MM"
    total_budget: float | None = None      # 总预算
    category_budgets: list[CategoryBudgetItem] = []  # 分类预算列表

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: str) -> str:
        if len(v) != 7 or v[4] != "-":
            raise ValueError("月份格式必须为 YYYY-MM")
        return v


class CategoryBudgetItem(BaseModel):
    """分类预算单项"""
    category_id: int
    amount: float


# ============================================================
# 预算响应
# ============================================================
class BudgetResponse(BaseModel):
    """预算查询响应"""
    month: str
    total_budget: BudgetItem | None = None
    category_budgets: list[BudgetItem] = []
