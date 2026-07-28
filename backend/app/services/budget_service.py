"""
预算业务逻辑层 — 月度预算的查询与设置。
"""
import logging
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.bill import Bill
from app.models.category import Category

logger = logging.getLogger("dailytracker.budget")


class BudgetService:
    """预算服务 — 设置/查询月度总预算和分类预算。"""

    @staticmethod
    async def get_budgets(db: AsyncSession, user_id: int, month: str) -> dict:
        """
        获取用户指定月份的预算。

        返回总预算 + 各分类预算及其已花费金额。
        """
        # 查询总预算
        total_budget = None
        total_result = await db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.month == month,
                Budget.category_id.is_(None),
            )
        )
        total_row = total_result.scalar_one_or_none()

        # 当月总支出
        year, month_num = map(int, month.split("-"))
        total_expense = await BudgetService._get_month_expense(db, user_id, year, month_num)

        if total_row:
            total_budget = {
                "category_id": None,
                "category_name": "总预算",
                "amount": float(total_row.amount),
                "spent": round(float(total_expense), 2),
                "usage_rate": round(float(total_expense) / float(total_row.amount), 2)
                if float(total_row.amount) > 0 else 0.0,
            }

        # 查询分类预算
        cat_result = await db.execute(
            select(Budget, Category.name, Category.icon)
            .join(Category, Budget.category_id == Category.id, isouter=True)
            .where(
                Budget.user_id == user_id,
                Budget.month == month,
                Budget.category_id.isnot(None),
            )
        )
        cat_rows = cat_result.all()

        category_budgets = []
        for budget, cat_name, cat_icon in cat_rows:
            # 计算该分类的已花费金额
            cat_expense = await db.scalar(
                select(func.coalesce(func.sum(Bill.amount), 0)).where(
                    Bill.user_id == user_id,
                    Bill.type == "expense",
                    Bill.category_id == budget.category_id,
                    func.extract("year", Bill.bill_date) == year,
                    func.extract("month", Bill.bill_date) == month_num,
                )
            ) or 0.0

            category_budgets.append({
                "category_id": budget.category_id,
                "category_name": cat_name or "未知分类",
                "amount": float(budget.amount),
                "spent": round(float(cat_expense), 2),
                "usage_rate": round(float(cat_expense) / float(budget.amount), 2)
                if float(budget.amount) > 0 else 0.0,
            })

        return {
            "month": month,
            "total_budget": total_budget,
            "category_budgets": category_budgets,
        }

    @staticmethod
    async def set_budgets(
        db: AsyncSession,
        user_id: int,
        month: str,
        total_budget: float | None = None,
        category_budgets: list[dict] | None = None,
    ) -> dict:
        """
        设置/更新预算 — 先删后插（该月份的全部预算）。

        参数 category_budgets: [{category_id, amount}, ...]
        """
        # 删除该月份所有已有预算
        await db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.month == month,
            )
        )
        existing = (await db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.month == month,
            )
        )).scalars().all()
        for b in existing:
            await db.delete(b)

        # 插入总预算
        if total_budget is not None and total_budget > 0:
            db.add(Budget(
                user_id=user_id,
                category_id=None,
                amount=round(float(total_budget), 2),
                month=month,
            ))

        # 插入分类预算
        if category_budgets:
            for item in category_budgets:
                if item.get("amount", 0) > 0:
                    db.add(Budget(
                        user_id=user_id,
                        category_id=item["category_id"],
                        amount=round(float(item["amount"]), 2),
                        month=month,
                    ))

        await db.flush()

        logger.info(f"预算更新成功: user={user_id} month={month}")

        # 返回更新后的预算数据
        return await BudgetService.get_budgets(db, user_id, month)

    # ============================================================
    # 内部方法
    # ============================================================
    @staticmethod
    async def _get_month_expense(db: AsyncSession, user_id: int, year: int, month: int) -> float:
        """获取用户某月总支出。"""
        result = await db.scalar(
            select(func.coalesce(func.sum(Bill.amount), 0)).where(
                Bill.user_id == user_id,
                Bill.type == "expense",
                func.extract("year", Bill.bill_date) == year,
                func.extract("month", Bill.bill_date) == month,
            )
        )
        return float(result or 0)
