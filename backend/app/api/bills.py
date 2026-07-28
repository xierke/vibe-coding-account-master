"""
账单 API 路由 — 记账 CRUD、批量删除、搜索。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.deps import get_db, get_current_user, get_current_user_id
from app.schemas.bill import (
    BillCreateRequest,
    BillUpdateRequest,
    BatchDeleteRequest,
    BillResponse,
    BillListResponse,
)
from app.schemas.common import APIResponse, PaginatedData
from app.services.bill_service import BillService
from app.services.home_service import HomeService

router = APIRouter(prefix="/bills", tags=["账单"])


# ============================================================
# 创建账单
# ============================================================
@router.post("", response_model=APIResponse[BillResponse], summary="记一笔")
async def create_bill(
    req: BillCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    创建收支账单 — 首页记账核心接口。
    金额保留 2 位小数，bill_date 为空时默认当天。
    """
    data = await BillService.create_bill(
        db,
        user_id=user_id,
        bill_type=req.type,
        amount=req.amount,
        category_id=req.category_id,
        bill_date=req.bill_date,
        note=req.note,
    )
    # 记一笔后清除主页缓存
    await HomeService.invalidate_cache(user_id)
    return APIResponse(data=data)


# ============================================================
# 账单列表
# ============================================================
@router.get("", response_model=APIResponse[PaginatedData[BillResponse]], summary="账单列表")
async def list_bills(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    type: str | None = Query(None, description="收入/支出: income|expense"),
    category_id: int | None = Query(None, description="分类 ID"),
    start_date: date | None = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: date | None = Query(None, description="结束日期 YYYY-MM-DD"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    账单列表 — 分页 + 多条件筛选。
    按 bill_date DESC 排序。
    """
    data = await BillService.get_bills(
        db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        bill_type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
    )
    return APIResponse(data=data)


# ============================================================
# 搜索账单 — 必须在 /{bill_id} 之前定义
# ============================================================
@router.get("/search", response_model=APIResponse[PaginatedData[BillResponse]], summary="搜索账单")
async def search_bills(
    keyword: str = Query("", description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    搜索账单 — 按备注文本模糊匹配，或金额精确匹配。
    """
    data = await BillService.search_bills(
        db,
        user_id=user_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return APIResponse(data=data)


# ============================================================
# 账单详情
# ============================================================
@router.get("/{bill_id}", response_model=APIResponse[BillResponse], summary="账单详情")
async def get_bill(
    bill_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取单条账单详情。"""
    data = await BillService.get_bill(db, bill_id, user_id)
    return APIResponse(data=data)


# ============================================================
# 编辑账单
# ============================================================
@router.put("/{bill_id}", response_model=APIResponse[BillResponse], summary="编辑账单")
async def update_bill(
    bill_id: int,
    req: BillUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """编辑账单 — 仅更新传入的非空字段。"""
    update_data = req.model_dump(exclude_none=True)
    data = await BillService.update_bill(db, bill_id, user_id, **update_data)
    # 编辑后清除主页缓存
    await HomeService.invalidate_cache(user_id)
    return APIResponse(data=data)


# ============================================================
# 删除账单
# ============================================================
@router.delete("/{bill_id}", response_model=APIResponse, summary="删除账单")
async def delete_bill(
    bill_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """删除单条账单。"""
    await BillService.delete_bill(db, bill_id, user_id)
    # 删除后清除主页缓存
    await HomeService.invalidate_cache(user_id)
    return APIResponse(message="删除成功")


# ============================================================
# 批量删除
# ============================================================
@router.post("/batch-delete", response_model=APIResponse, summary="批量删除账单")
async def batch_delete(
    req: BatchDeleteRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """批量删除账单 — 仅删除属于当前用户的账单。"""
    count = await BillService.batch_delete_bills(db, req.ids, user_id)
    await HomeService.invalidate_cache(user_id)
    return APIResponse(message=f"成功删除 {count} 条账单")
