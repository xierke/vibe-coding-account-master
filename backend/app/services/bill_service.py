"""
账单业务逻辑层 — 记账 CRUD、批量删除、搜索。
"""
import logging
from datetime import date, datetime

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.bill import Bill
from app.models.category import Category
from app.exceptions import NotFoundError, ForbiddenError, ValidationError

logger = logging.getLogger("dailytracker.bill")


class BillService:
    """账单服务 — 处理所有账单 CRUD 操作。"""

    # ============================================================
    # 创建账单
    # ============================================================
    @staticmethod
    async def create_bill(
        db: AsyncSession,
        user_id: int,
        bill_type: str,
        amount: float,
        category_id: int,
        bill_date: date | None = None,
        note: str | None = None,
    ) -> dict:
        """
        记一笔 — 创建收支记录。

        规则：
        - bill_date 为空时默认当天
        - 必须校验 category_id 是否存在
        - 金额保留 2 位小数
        """
        # 校验分类存在
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if category is None:
            raise NotFoundError("分类不存在")

        bill = Bill(
            user_id=user_id,
            type=bill_type,
            amount=round(float(amount), 2),
            category_id=category_id,
            bill_date=bill_date or date.today(),
            note=note,
        )
        db.add(bill)
        await db.flush()
        await db.refresh(bill)

        # 重新查询关联数据（category）
        result = await db.execute(
            select(Bill).options(joinedload(Bill.category)).where(Bill.id == bill.id)
        )
        bill = result.scalar_one()

        logger.info(f"账单创建成功: id={bill.id} type={bill_type} amount={amount}")

        return BillService._bill_to_dict(bill)

    # ============================================================
    # 查询账单列表
    # ============================================================
    @staticmethod
    async def get_bills(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        bill_type: str | None = None,
        category_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        """
        获取账单列表 — 分页 + 多条件筛选。

        排序：bill_date DESC, created_at DESC
        """
        conditions = [Bill.user_id == user_id]

        if bill_type:
            conditions.append(Bill.type == bill_type)
        if category_id:
            conditions.append(Bill.category_id == category_id)
        if start_date:
            conditions.append(Bill.bill_date >= start_date)
        if end_date:
            conditions.append(Bill.bill_date <= end_date)

        where_clause = and_(*conditions)

        # 查询总数
        count_result = await db.execute(select(func.count(Bill.id)).where(where_clause))
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        query = (
            select(Bill)
            .options(joinedload(Bill.category))
            .where(where_clause)
            .order_by(Bill.bill_date.desc(), Bill.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        bills = result.unique().scalars().all()

        return {
            "items": [BillService._bill_to_dict(b) for b in bills],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ============================================================
    # 查询账单详情
    # ============================================================
    @staticmethod
    async def get_bill(db: AsyncSession, bill_id: int, user_id: int) -> dict:
        """获取单条账单详情。"""
        bill = await BillService._get_user_bill(db, bill_id, user_id)
        return BillService._bill_to_dict(bill)

    # ============================================================
    # 编辑账单
    # ============================================================
    @staticmethod
    async def update_bill(
        db: AsyncSession,
        bill_id: int,
        user_id: int,
        **kwargs,
    ) -> dict:
        """编辑账单 — 仅更新传入的字段。"""
        bill = await BillService._get_user_bill(db, bill_id, user_id)

        for field, value in kwargs.items():
            if value is not None:
                if field == "amount":
                    value = round(float(value), 2)
                setattr(bill, field, value)

        await db.flush()
        await db.refresh(bill)

        # 重新查询带关联
        result = await db.execute(
            select(Bill).options(joinedload(Bill.category)).where(Bill.id == bill_id)
        )
        bill = result.scalar_one()

        return BillService._bill_to_dict(bill)

    # ============================================================
    # 删除账单
    # ============================================================
    @staticmethod
    async def delete_bill(db: AsyncSession, bill_id: int, user_id: int) -> None:
        """删除单条账单。"""
        bill = await BillService._get_user_bill(db, bill_id, user_id)
        await db.delete(bill)
        await db.flush()
        logger.info(f"账单已删除: id={bill_id}")

    # ============================================================
    # 批量删除
    # ============================================================
    @staticmethod
    async def batch_delete_bills(db: AsyncSession, ids: list[int], user_id: int) -> int:
        """
        批量删除账单 — 仅删除属于当前用户的账单。

        返回实际删除的数量。
        """
        result = await db.execute(
            select(Bill).where(
                Bill.id.in_(ids),
                Bill.user_id == user_id,
            )
        )
        bills = result.scalars().all()

        count = 0
        for bill in bills:
            await db.delete(bill)
            count += 1

        await db.flush()
        logger.info(f"批量删除账单: {count}/{len(ids)} 条")
        return count

    # ============================================================
    # 搜索账单
    # ============================================================
    @staticmethod
    async def search_bills(
        db: AsyncSession,
        user_id: int,
        keyword: str = "",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        搜索账单 — 按备注文本 + 金额范围搜索。

        搜索范围：备注文本模糊匹配、金额精确匹配。
        """
        conditions = [Bill.user_id == user_id]

        if keyword:
            # 尝试解析金额
            keyword_condition = Bill.note.like(f"%{keyword}%")
            try:
                amount_val = float(keyword)
                keyword_condition = or_(
                    keyword_condition,
                    Bill.amount == amount_val,
                )
            except ValueError:
                pass
            conditions.append(keyword_condition)

        where_clause = and_(*conditions)

        count_result = await db.execute(select(func.count(Bill.id)).where(where_clause))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        query = (
            select(Bill)
            .options(joinedload(Bill.category))
            .where(where_clause)
            .order_by(Bill.bill_date.desc(), Bill.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        bills = result.unique().scalars().all()

        return {
            "items": [BillService._bill_to_dict(b) for b in bills],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ============================================================
    # 内部方法
    # ============================================================
    @staticmethod
    async def _get_user_bill(db: AsyncSession, bill_id: int, user_id: int) -> Bill:
        """获取属于当前用户的账单，不存在则抛 NotFoundError。"""
        result = await db.execute(
            select(Bill)
            .options(joinedload(Bill.category))
            .where(Bill.id == bill_id)
        )
        bill = result.scalar_one_or_none()

        if bill is None:
            raise NotFoundError("账单不存在")
        if bill.user_id != user_id:
            raise ForbiddenError("无权访问此账单")

        return bill

    @staticmethod
    def _bill_to_dict(bill: Bill) -> dict:
        """将 Bill ORM 对象转为响应 dict。"""
        return {
            "id": bill.id,
            "type": bill.type,
            "amount": float(bill.amount),
            "category": {
                "id": bill.category.id,
                "name": bill.category.name,
                "icon": bill.category.icon,
                "color": bill.category.color,
            } if bill.category else None,
            "bill_date": str(bill.bill_date),
            "note": bill.note,
            "created_at": bill.created_at.isoformat() if bill.created_at else "",
            "updated_at": bill.updated_at.isoformat() if bill.updated_at else "",
        }
