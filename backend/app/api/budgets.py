"""
预算 API 路由 — 查询和设置月度预算。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_id
from app.schemas.common import APIResponse
from app.schemas.budget import BudgetSetRequest, BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["预算"])


# ============================================================
# 获取预算
# ============================================================
@router.get("", response_model=APIResponse[BudgetResponse], summary="获取预算")
async def get_budgets(
    month: str = Query(..., description="月份 YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户指定月份的预算 — 包括总预算和各分类预算及其执行情况。
    """
    data = await BudgetService.get_budgets(db, user_id, month)
    return APIResponse(data=data)


# ============================================================
# 设置/更新预算
# ============================================================
@router.put("", response_model=APIResponse[BudgetResponse], summary="设置预算")
async def set_budgets(
    req: BudgetSetRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    设置/更新月度预算 — 先删后插该月份所有预算数据。
    可同时设置总预算和分类预算。
    """
    category_budgets = [
        {"category_id": item.category_id, "amount": item.amount}
        for item in req.category_budgets
    ]
    data = await BudgetService.set_budgets(
        db,
        user_id=user_id,
        month=req.month,
        total_budget=req.total_budget,
        category_budgets=category_budgets,
    )
    return APIResponse(data=data)
