"""
用户 API 路由 — 个人信息查询/更新 + 主页 Dashboard。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, get_current_user_id
from app.schemas.common import APIResponse
from app.schemas.user import UserProfileResponse, UserProfileUpdateRequest, HomeDashboardResponse
from app.services.home_service import HomeService

router = APIRouter(tags=["用户 & 首页"])


# ============================================================
# 主页 Dashboard
# ============================================================
@router.get("/home", response_model=APIResponse[HomeDashboardResponse], summary="主页Dashboard")
async def get_home_dashboard(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    主页 Dashboard — 含本月收支概览、今日统计、预算进度、最近账单。
    使用 Redis 缓存（TTL 5 分钟），记账/编辑/删除后自动失效。
    """
    data = await HomeService.get_dashboard(db, user_id)
    return APIResponse(data=data)


# ============================================================
# 个人信息
# ============================================================
@router.get("/users/profile", response_model=APIResponse[UserProfileResponse], summary="个人信息")
async def get_profile(current_user=Depends(get_current_user)):
    """获取当前登录用户的个人信息。"""
    return APIResponse(data={
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else "",
    })


@router.put("/users/profile", response_model=APIResponse[UserProfileResponse], summary="更新个人信息")
async def update_profile(
    req: UserProfileUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前登录用户的个人信息 — 用户名、头像。"""
    if req.username is not None:
        # 检查用户名唯一性
        from sqlalchemy import select
        from app.models.user import User
        from app.exceptions import ConflictError

        existing = await db.execute(
            select(User).where(User.username == req.username, User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise ConflictError("用户名已被占用")
        current_user.username = req.username

    if req.avatar_url is not None:
        current_user.avatar_url = req.avatar_url

    await db.flush()
    await db.refresh(current_user)

    return APIResponse(data={
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else "",
    })
