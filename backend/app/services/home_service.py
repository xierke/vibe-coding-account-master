"""
主页 Dashboard 服务 — 聚合本月收支概览 + 最近账单 + 预算进度。
使用 Redis 缓存（Cache-Aside 模式），写操作时清除相关缓存。
"""
import json
import logging
from datetime import date, datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.bill import Bill
from app.models.budget import Budget
from app.core.redis import cache_get, cache_set, cache_delete

logger = logging.getLogger("dailytracker.home")

HOME_CACHE_KEY = "home:dashboard:{user_id}"
HOME_CACHE_TTL = 300  # 5 分钟


class HomeService:
    """主页服务 — 返回 Dashboard 聚合数据。"""

    @staticmethod
    async def get_dashboard(db: AsyncSession, user_id: int) -> dict:
        """
        获取主页 Dashboard 数据。

        缓存策略：先查 Redis → 未命中则查 DB → 写入 Redis。
        """
        # 1. 尝试从缓存读取
        cache_key = HOME_CACHE_KEY.format(user_id=user_id)
        cached = await cache_get(cache_key)
        if cached:
            logger.debug(f"主页数据缓存命中: user={user_id}")
            return json.loads(cached)

        # 2. 缓存未命中 → 查数据库
        today = date.today()
        year = today.year
        month = today.month
        month_str = f"{year}-{month:02d}"

        # 本月收支概览
        month_income = await db.scalar(
            select(func.coalesce(func.sum(Bill.amount), 0)).where(
                Bill.user_id == user_id,
                Bill.type == "income",
                func.extract("year", Bill.bill_date) == year,
                func.extract("month", Bill.bill_date) == month,
            )
        ) or 0.0

        month_expense = await db.scalar(
            select(func.coalesce(func.sum(Bill.amount), 0)).where(
                Bill.user_id == user_id,
                Bill.type == "expense",
                func.extract("year", Bill.bill_date) == year,
                func.extract("month", Bill.bill_date) == month,
            )
        ) or 0.0

        # 今日账单数 + 今日支出
        today_bill_count = await db.scalar(
            select(func.count(Bill.id)).where(
                Bill.user_id == user_id,
                Bill.bill_date == today,
            )
        ) or 0

        today_expense = await db.scalar(
            select(func.coalesce(func.sum(Bill.amount), 0)).where(
                Bill.user_id == user_id,
                Bill.type == "expense",
                Bill.bill_date == today,
            )
        ) or 0.0

        # 预算进度
        budget_total = None
        budget_usage_rate = 0.0
        budget_warning = False

        budget_result = await db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.month == month_str,
                Budget.category_id.is_(None),
            )
        )
        budget_row = budget_result.scalar_one_or_none()
        if budget_row:
            budget_total = float(budget_row.amount)
            budget_usage_rate = round(float(month_expense) / budget_total, 2) if budget_total > 0 else 0.0
            budget_warning = budget_usage_rate >= 0.8

        # 最近 5 条账单
        recent_result = await db.execute(
            select(Bill)
            .options(joinedload(Bill.category))
            .where(Bill.user_id == user_id)
            .order_by(Bill.bill_date.desc(), Bill.created_at.desc())
            .limit(5)
        )
        recent_bills = recent_result.unique().scalars().all()

        recent_items = []
        for b in recent_bills:
            recent_items.append({
                "id": b.id,
                "type": b.type,
                "amount": float(b.amount),
                "category_name": b.category.name if b.category else "",
                "category_icon": b.category.icon if b.category else "",
                "category_color": b.category.color if b.category else "",
                "bill_date": str(b.bill_date),
                "note": b.note,
            })

        # 3. 组装响应
        dashboard = {
            "month_income": round(float(month_income), 2),
            "month_expense": round(float(month_expense), 2),
            "month_balance": round(float(month_income) - float(month_expense), 2),
            "today_bill_count": today_bill_count,
            "today_expense": round(float(today_expense), 2),
            "budget_total": budget_total,
            "budget_spent": round(float(month_expense), 2),
            "budget_usage_rate": budget_usage_rate,
            "budget_warning": budget_warning,
            "recent_bills": recent_items,
        }

        # 4. 写入缓存
        await cache_set(cache_key, json.dumps(dashboard, ensure_ascii=False), HOME_CACHE_TTL)

        logger.debug(f"主页数据已缓存: user={user_id}")
        return dashboard

    @staticmethod
    async def invalidate_cache(user_id: int):
        """使指定用户的主页缓存失效 — 在创建/编辑/删除账单后调用。"""
        cache_key = HOME_CACHE_KEY.format(user_id=user_id)
        await cache_delete(cache_key)
