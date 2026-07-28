"""
报表 API 路由 — 周报、月报、自定义时间报表。
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_id
from app.schemas.common import APIResponse
from app.schemas.report import (
    WeeklyReportResponse,
    MonthlyReportResponse,
    CustomReportResponse,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["报表"])


# ============================================================
# 周报表
# ============================================================
@router.get("/weekly", response_model=APIResponse[WeeklyReportResponse], summary="周报表")
async def weekly_report(
    date_param: date = Query(..., alias="date", description="参考日期 YYYY-MM-DD"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    周收支报表 — 返回该日期所在周的数据。
    包含：概览、每日收支柱状图、支出分类饼图、周对比。
    """
    data = await ReportService.get_weekly_report(db, user_id, date_param)
    return APIResponse(data=data)


# ============================================================
# 月报表
# ============================================================
@router.get("/monthly", response_model=APIResponse[MonthlyReportResponse], summary="月报表")
async def monthly_report(
    month: str = Query(..., description="月份 YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    月收支报表。
    包含：概览、每日趋势折线图、支出分类排行、消费日历热力图、月对比。
    """
    data = await ReportService.get_monthly_report(db, user_id, month)
    return APIResponse(data=data)


# ============================================================
# 自定义时间报表
# ============================================================
@router.get("/custom", response_model=APIResponse[CustomReportResponse], summary="自定义报表")
async def custom_report(
    start_date: date = Query(..., description="起始日期 YYYY-MM-DD"),
    end_date: date = Query(..., description="结束日期 YYYY-MM-DD"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    自定义时间范围报表 — 格式同月报。
    """
    data = await ReportService.get_custom_report(db, user_id, start_date, end_date)
    return APIResponse(data=data)
