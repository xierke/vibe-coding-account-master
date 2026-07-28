"""
认证模块 Schema — 注册、登录、Token 刷新、验证码、密码重置。
"""
from pydantic import BaseModel, EmailStr, field_validator
import re


# ============================================================
# 注册
# ============================================================
class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str          # 用户名 2-20 字符
    email: EmailStr        # 邮箱
    password: str          # 密码 8-20 位，含大小写字母+数字
    confirm_password: str  # 确认密码

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 20:
            raise ValueError("用户名长度需在 2-20 个字符之间")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码长度需在 8-20 个字符之间")
        if not re.search(r'[A-Z]', v) and not re.search(r'[a-z]', v):
            raise ValueError("密码需包含英文字母")
        if not re.search(r'[a-z]', v):
            pass  # allow uppercase only
        if not re.search(r'\d', v):
            raise ValueError("密码需包含数字")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v


class RegisterResponse(BaseModel):
    """注册成功返回 — 自动登录，返回 Token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


# ============================================================
# 密码登录
# ============================================================
class LoginRequest(BaseModel):
    """密码登录请求 — 支持用户名或邮箱"""
    account: str           # 用户名或邮箱
    password: str
    remember_me: bool = False  # 是否记住登录（影响 refresh_token 有效期）


class LoginResponse(BaseModel):
    """登录成功返回"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


# ============================================================
# 短信验证码登录
# ============================================================
class SmsLoginRequest(BaseModel):
    """短信验证码登录请求"""
    phone: str
    code: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("手机号格式不正确")
        return v


# ============================================================
# Token 刷新
# ============================================================
class RefreshRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class RefreshResponse(BaseModel):
    """刷新 Token 返回"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ============================================================
# 发送验证码
# ============================================================
class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    type: str              # "email" 或 "sms"
    target: str            # 邮箱地址或手机号

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("email", "sms"):
            raise ValueError("type 必须为 email 或 sms")
        return v


# ============================================================
# 密码重置
# ============================================================
class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr
    code: str              # 验证码
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码长度需在 8-20 个字符之间")
        if not re.search(r'\d', v):
            raise ValueError("密码需包含数字")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v


# ============================================================
# 修改密码（已登录）
# ============================================================
class ChangePasswordRequest(BaseModel):
    """已登录用户修改密码"""
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v
