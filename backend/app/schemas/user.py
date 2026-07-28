"""
用户模块 Schema — 个人资料、主页 Dashboard。
"""
from datetime import datetime
from pydantic import BaseModel, field_validator


# ============================================================
# 用户个人资料
# ============================================================
class UserProfileResponse(BaseModel):
    """用户个人信息响应"""
    id: int
    username: str
    email: str
    phone: str | None = None
    avatar_url: str | None = None
    created_at: str

    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    """更新个人信息请求"""
    username: str | None = None
    avatar_url: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 20:
                raise ValueError("用户名长度需在 2-20 个字符之间")
        return v


# ============================================================
# 主页 Dashboard
# ============================================================
class RecentBillItem(BaseModel):
    """主页最近账单条目"""
    id: int
    type: str
    amount: float
    category_name: str
    category_icon: str
    category_color: str
    bill_date: str
    note: str | None = None


class HomeDashboardResponse(BaseModel):
    """主页 Dashboard 数据"""
    # 本月概览
    month_income: float
    month_expense: float
    month_balance: float
    # 今日统计
    today_bill_count: int
    today_expense: float
    # 预算进度
    budget_total: float | None = None       # 月度总预算
    budget_spent: float = 0.0               # 本月已支出
    budget_usage_rate: float = 0.0           # 预算使用率 0.0~1.0
    budget_warning: bool = False             # 是否超过 80%
    # 最近账单
    recent_bills: list[RecentBillItem] = []
