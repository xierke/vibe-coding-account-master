"""
账单模型 — bills 表。
每一条收入/支出记录。
"""
from datetime import datetime, date

from sqlalchemy import String, Integer, DateTime, Date, Numeric, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Bill(Base):
    """账单表 ORM 模型"""

    __tablename__ = "bills"

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键")

    # --- 所属用户 ---
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="所属用户"
    )

    # --- 账单核心字段 ---
    type: Mapped[str] = mapped_column(
        SAEnum("income", "expense", name="bill_type"), nullable=False, comment="收入/支出"
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="金额 (0.01 ~ 999,999,999.99)"
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, comment="分类"
    )
    bill_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="账单日期"
    )
    note: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="备注"
    )

    # --- 时间戳 ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间"
    )

    # --- 关联关系 ---
    user = relationship("User", back_populates="bills")
    category = relationship("Category", back_populates="bills")

    def __repr__(self) -> str:
        return f"<Bill id={self.id} type={self.type} amount={self.amount}>"
