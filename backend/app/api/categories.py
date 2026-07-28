"""
分类 API 路由 — 分类列表、创建、编辑、删除。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, get_current_user_id
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
)
from app.schemas.common import APIResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["分类"])


# ============================================================
# 分类列表
# ============================================================
@router.get("", response_model=APIResponse[list[CategoryResponse]], summary="分类列表")
async def list_categories(
    type: str | None = Query(None, description="收入/支出: income|expense"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取分类列表 — 系统默认 + 用户自定义。
    可通过 type 参数筛选收入或支出分类。
    """
    data = await CategoryService.get_categories(db, user_id, type_filter=type)
    return APIResponse(data=data)


# ============================================================
# 创建自定义分类
# ============================================================
@router.post("", response_model=APIResponse[CategoryResponse], summary="创建自定义分类")
async def create_category(
    req: CategoryCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建用户自定义分类 — 需指定名称、图标、颜色、类型。"""
    data = await CategoryService.create_category(
        db,
        user_id=user_id,
        name=req.name,
        icon=req.icon,
        color=req.color,
        cat_type=req.type,
        sort_order=req.sort_order,
    )
    return APIResponse(data=data)


# ============================================================
# 编辑分类
# ============================================================
@router.put("/{category_id}", response_model=APIResponse[CategoryResponse], summary="编辑分类")
async def update_category(
    category_id: int,
    req: CategoryUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """编辑分类 — 仅更新传入的非空字段。"""
    update_data = req.model_dump(exclude_none=True)
    data = await CategoryService.update_category(db, category_id, user_id, **update_data)
    return APIResponse(data=data)


# ============================================================
# 删除分类
# ============================================================
@router.delete("/{category_id}", response_model=APIResponse, summary="删除分类")
async def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    删除分类。
    系统默认分类不可删除，有账单关联的分类不可删除。
    """
    await CategoryService.delete_category(db, category_id, user_id)
    return APIResponse(message="删除成功")
