"""
预算模型 — budgets 表。
月度总预算 + 分类预算。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Budget(Base):
    """预算表 ORM 模型"""

    __tablename__ = "budgets"

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键")

    # --- 所属用户 ---
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="所属用户"
    )

    # --- 预算维度 ---
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True,
        comment="分类，NULL=月度总预算"
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="预算金额"
    )
    month: Mapped[str] = mapped_column(
        String(7), nullable=False, comment="预算月份 YYYY-MM"
    )

    # --- 时间戳 ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # --- 关联关系 ---
    user = relationship("User", back_populates="budgets")

    def __repr__(self) -> str:
        return f"<Budget id={self.id} month={self.month} amount={self.amount}>"
