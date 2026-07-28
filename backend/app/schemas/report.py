"""
报表模块 Schema — 周报、月报、自定义报表的响应结构。
"""
from pydantic import BaseModel


# ============================================================
# 概览卡片 — 所有报表共有
# ============================================================
class ReportOverview(BaseModel):
    """报表概览数据"""
    total_income: float       # 总收入
    total_expense: float      # 总支出
    balance: float            # 结余 = 收入 - 支出
    avg_daily_expense: float  # 日均支出
    budget_usage_rate: float | None = None  # 预算使用率 (仅月报，有预算时)


# ============================================================
# 每日收支数据 — 柱状图/折线图用
# ============================================================
class DailySummary(BaseModel):
    """单日收支汇总"""
    date: str                 # "MM-DD" 或 "YYYY-MM-DD"
    income: float = 0.0       # 当天收入
    expense: float = 0.0      # 当天支出


# ============================================================
# 支出分类占比 — 饼图用
# ============================================================
class CategoryPieItem(BaseModel):
    """饼图单个分类数据"""
    category_id: int
    category_name: str
    icon: str
    color: str
    amount: float             # 该分类总金额
    percentage: float         # 占比百分比


# ============================================================
# 分类排行 — 条形图用
# ============================================================
class CategoryRankItem(BaseModel):
    """排行单条数据"""
    rank: int
    category_id: int
    category_name: str
    icon: str
    color: str
    amount: float
    percentage: float


# ============================================================
# 热力图数据 — 月报用
# ============================================================
class CalendarDay(BaseModel):
    """消费日历单日数据"""
    date: str                 # "YYYY-MM-DD"
    day_of_month: int         # 1-31
    day_of_week: int          # 0=周一 ... 6=周日
    amount: float = 0.0       # 当日支出金额
    intensity: float = 0.0    # 热力强度 0.0 ~ 1.0（相对最高支出）


# ============================================================
# 周期对比 — 环比变化
# ============================================================
class PeriodComparison(BaseModel):
    """周期对比数据"""
    prev_income: float        # 上期收入
    prev_expense: float       # 上期支出
    income_change_pct: float  # 收入环比变化 (如 +15.3 或 -5.2)
    expense_change_pct: float # 支出环比变化


# ============================================================
# 周报响应
# ============================================================
class WeeklyReportResponse(BaseModel):
    """周收支报表"""
    week_start: str           # 本周起始日期 "YYYY-MM-DD"
    week_end: str             # 本周结束日期
    overview: ReportOverview
    daily_data: list[DailySummary]        # 每日收支（7天）
    category_pie: list[CategoryPieItem]   # 支出分类占比
    comparison: PeriodComparison | None = None  # 周对比


# ============================================================
# 月报响应
# ============================================================
class MonthlyReportResponse(BaseModel):
    """月收支报表"""
    month: str                # "YYYY-MM"
    overview: ReportOverview
    daily_data: list[DailySummary]          # 每日收支（该月所有日期）
    category_ranks: list[CategoryRankItem]  # 支出分类排行 Top 10
    calendar_data: list[CalendarDay]        # 消费日历热力图
    comparison: PeriodComparison | None = None  # 月对比


# ============================================================
# 自定义报表响应 — 同月报格式
# ============================================================
class CustomReportResponse(BaseModel):
    """自定义时间范围报表"""
    start_date: str           # "YYYY-MM-DD"
    end_date: str             # "YYYY-MM-DD"
    overview: ReportOverview
    daily_data: list[DailySummary]
    category_ranks: list[CategoryRankItem]
