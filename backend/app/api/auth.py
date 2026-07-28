"""
认证 API 路由 — 注册、登录、短信登录、Token 刷新、验证码、密码管理。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    SmsLoginRequest,
    RefreshRequest,
    RefreshResponse,
    SendCodeRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


# ============================================================
# 注册
# ============================================================
@router.post("/register", response_model=APIResponse[RegisterResponse], summary="用户注册")
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    邮箱注册 — 注册成功自动登录，返回 access_token + refresh_token。
    """
    data = await AuthService.register(
        db,
        username=req.username,
        email=str(req.email),
        password=req.password,
    )
    return APIResponse(data=data)


# ============================================================
# 密码登录
# ============================================================
@router.post("/login", response_model=APIResponse[LoginResponse], summary="密码登录")
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    密码登录 — 支持用户名或邮箱。
    密码错误超过 5 次账号锁定 15 分钟。
    """
    data = await AuthService.login(
        db,
        account=req.account,
        password=req.password,
        remember_me=req.remember_me,
    )
    return APIResponse(data=data)


# ============================================================
# 短信验证码登录
# ============================================================
@router.post("/login/sms", response_model=APIResponse[LoginResponse], summary="短信验证码登录")
async def login_by_sms(
    req: SmsLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    短信验证码登录 — 首次登录自动创建/绑定账号。
    """
    data = await AuthService.login_by_sms(
        db,
        phone=req.phone,
        code=req.code,
    )
    return APIResponse(data=data)


# ============================================================
# Token 刷新
# ============================================================
@router.post("/refresh", response_model=APIResponse[RefreshResponse], summary="刷新Token")
async def refresh(
    req: RefreshRequest,
):
    """
    使用 refresh_token 获取新的 access_token + refresh_token。
    """
    data = await AuthService.refresh_token(req.refresh_token)
    return APIResponse(data=data)


# ============================================================
# 发送验证码
# ============================================================
@router.post("/send-code", response_model=APIResponse, summary="发送验证码")
async def send_code(req: SendCodeRequest):
    """
    发送验证码 — type: "email" | "sms"。
    邮箱：发送到指定邮箱（Mock）；
    短信：发送到指定手机号（Mock）。
    验证码有效期 5 分钟。
    """
    await AuthService.send_verify_code(req.target, req.type)
    return APIResponse(message="验证码已发送")


# ============================================================
# 密码重置
# ============================================================
@router.post("/reset-password", response_model=APIResponse, summary="重置密码")
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    通过验证码重置密码 — 需要邮箱 + 验证码。
    重置成功后需重新登录。
    """
    await AuthService.reset_password(
        db,
        email=str(req.email),
        code=req.code,
        new_password=req.new_password,
    )
    return APIResponse(message="密码重置成功，请重新登录")


# ============================================================
# 修改密码（已登录）
# ============================================================
@router.put("/password", response_model=APIResponse, summary="修改密码")
async def change_password(
    req: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    已登录用户修改密码 — 需提供原密码。
    """
    await AuthService.change_password(
        db,
        user=current_user,
        old_password=req.old_password,
        new_password=req.new_password,
    )
    return APIResponse(message="密码修改成功")
