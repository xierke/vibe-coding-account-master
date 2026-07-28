"""
分类模型 — categories 表。
系统默认分类 (user_id=NULL) + 用户自定义分类。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

class Category(Base):
    """收支分类表 ORM 模型"""

    __tablename__ = "categories"

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键")

    # --- 所属用户 ---
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True,
        comment="所属用户，NULL=系统默认分类"
    )

    # --- 分类属性 ---
    name: Mapped[str] = mapped_column(String(30), nullable=False, comment="分类名称")
    icon: Mapped[str] = mapped_column(String(50), nullable=False, comment="图标 (emoji)")
    color: Mapped[str] = mapped_column(String(7), nullable=False, comment="颜色 #RRGGBB")
    type: Mapped[str] = mapped_column(
        SAEnum("income", "expense", name="category_type"), nullable=False, comment="收入/支出类型"
    )

    # --- 标记 ---
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否系统默认")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序值，越小越靠前")

    # --- 时间戳 ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )

    # --- 关联关系 ---
    user = relationship("User", back_populates="categories")
    bills = relationship("Bill", back_populates="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r} type={self.type}>"
