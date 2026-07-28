"""
用户模型 — users 表。
存储注册用户的基本信息，支持邮箱注册 + 手机号绑定。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class User(Base):
    """用户表 ORM 模型"""

    __tablename__ = "users"

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键")

    # --- 基本信息 ---
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名，唯一")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="邮箱，唯一")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="bcrypt 密码哈希")

    # --- 手机号 — 支持短信验证码登录 ---
    phone: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, comment="手机号，首次短信登录时绑定"
    )

    # --- 头像 ---
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="头像 URL")

    # --- 安全相关 — 登录锁定 ---
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, comment="账号是否被锁定")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="锁定到期时间")
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, comment="连续登录失败次数")

    # --- 时间戳 ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间"
    )

    # --- 关联关系 ---
    bills = relationship("Bill", back_populates="user", lazy="dynamic")
    categories = relationship("Category", back_populates="user", lazy="dynamic")
    budgets = relationship("Budget", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
