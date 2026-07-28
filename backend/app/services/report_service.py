"""
报表业务逻辑层 — 周报、月报、自定义时间报表。
所有报表计算均为实时查询（不缓存），确保数据准确。
"""
import logging
from datetime import date, datetime, timedelta
from calendar import monthrange, day_name

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.models.category import Category
from app.models.budget import Budget

logger = logging.getLogger("dailytracker.report")


class ReportService:
    """报表服务 — 聚合计算收支数据，返回图表就绪的 JSON。"""

    # ============================================================
    # 周报表
    # ============================================================
    @staticmethod
    async def get_weekly_report(db: AsyncSession, user_id: int, ref_date: date) -> dict:
        """
        获取周收支报表。

        参数 ref_date — 指定日期，返回该日期所在周的周报（周一～周日）。
        """
        # 计算本周范围
        monday = ref_date - timedelta(days=ref_date.weekday())
        sunday = monday + timedelta(days=6)

        # 上周范围
        prev_monday = monday - timedelta(days=7)
        prev_sunday = monday - timedelta(days=1)

        # 1. 概览 + 每日数据
        overview, daily_data = await ReportService._calc_period_summary(
            db, user_id, monday, sunday
        )

        # 2. 支出分类占比（饼图）
        category_pie = await ReportService._calc_category_pie(
            db, user_id, monday, sunday
        )

        # 3. 周对比
        prev_overview, _ = await ReportService._calc_period_summary(
            db, user_id, prev_monday, prev_sunday
        )
        comparison = ReportService._calc_comparison(overview, prev_overview)

        return {
            "week_start": str(monday),
            "week_end": str(sunday),
            "overview": overview,
            "daily_data": daily_data,
            "category_pie": category_pie,
            "comparison": comparison,
        }

    # ============================================================
    # 月报表
    # ============================================================
    @staticmethod
    async def get_monthly_report(db: AsyncSession, user_id: int, month: str) -> dict:
        """
        获取月收支报表。

        参数 month — "YYYY-MM" 格式。
        """
        year, month_num = map(int, month.split("-"))
        first_day = date(year, month_num, 1)
        _, last_day_num = monthrange(year, month_num)
        last_day = date(year, month_num, last_day_num)

        # 上月范围
        if month_num == 1:
            prev_first = date(year - 1, 12, 1)
            prev_last = date(year - 1, 12, 31)
        else:
            prev_first = date(year, month_num - 1, 1)
            _, prev_last_num = monthrange(year, month_num - 1)
            prev_last = date(year, month_num - 1, prev_last_num)

        # 1. 概览 + 每日数据
        overview, daily_data = await ReportService._calc_period_summary(
            db, user_id, first_day, last_day, include_all_days=True, month=first_day
        )

        # 2. 预算使用率
        budget_result = await db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.month == month,
                Budget.category_id.is_(None),  # 总预算
            )
        )
        budget = budget_result.scalar_one_or_none()
        if budget:
            overview["budget_usage_rate"] = round(
                (overview["total_expense"] / float(budget.amount)) * 100, 1
            )

        # 3. 支出分类排行 Top 10
        category_ranks = await ReportService._calc_category_ranks(
            db, user_id, first_day, last_day
        )

        # 4. 消费日历热力图
        calendar_data = await ReportService._calc_calendar_heatmap(
            db, user_id, first_day, last_day
        )

        # 5. 月度对比
        prev_overview, _ = await ReportService._calc_period_summary(
            db, user_id, prev_first, prev_last
        )
        comparison = ReportService._calc_comparison(overview, prev_overview)

        return {
            "month": month,
            "overview": overview,
            "daily_data": daily_data,
            "category_ranks": category_ranks,
            "calendar_data": calendar_data,
            "comparison": comparison,
        }

    # ============================================================
    # 自定义时间报表
    # ============================================================
    @staticmethod
    async def get_custom_report(
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> dict:
        """获取自定义时间范围报表，格式同月报。"""
        # 1. 概览 + 每日数据
        overview, daily_data = await ReportService._calc_period_summary(
            db, user_id, start_date, end_date, include_all_days=True, month=start_date
        )

        # 2. 支出分类排行 Top 10
        category_ranks = await ReportService._calc_category_ranks(
            db, user_id, start_date, end_date
        )

        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "overview": overview,
            "daily_data": daily_data,
            "category_ranks": category_ranks,
        }

    # ============================================================
    # 内部聚合方法
    # ============================================================

    @staticmethod
    async def _calc_period_summary(
        db: AsyncSession,
        user_id: int,
        start: date,
        end: date,
        include_all_days: bool = False,
        month: date | None = None,
    ) -> tuple[dict, list[dict]]:
        """
        计算时间段的收支概览和每日数据。

        参数 include_all_days — 是否补全缺失的日期（月报需要补全 1-31 所有日期）
        """
        # 聚合查询：按日期分组汇总
        base_conditions = [
            Bill.user_id == user_id,
            Bill.bill_date >= start,
            Bill.bill_date <= end,
        ]

        # 总收支
        total_income = await db.scalar(
            select(func.coalesce(func.sum(Bill.amount), 0)).where(
                and_(Bill.type == "income", *base_conditions)
            )
        ) or 0.0
        total_expense = await db.scalar(
            select(func.coalesce(func.sum(Bill.amount), 0)).where(
                and_(Bill.type == "expense", *base_conditions)
            )
        ) or 0.0

        days_count = (end - start).days + 1
        avg_daily = round(total_expense / days_count, 2) if days_count > 0 else 0.0

        overview = {
            "total_income": round(float(total_income), 2),
            "total_expense": round(float(total_expense), 2),
            "balance": round(float(total_income) - float(total_expense), 2),
            "avg_daily_expense": avg_daily,
            "budget_usage_rate": None,
        }

        # 每日数据
        result = await db.execute(
            select(
                Bill.bill_date,
                Bill.type,
                func.coalesce(func.sum(Bill.amount), 0).label("amount"),
            )
            .where(and_(*base_conditions))
            .group_by(Bill.bill_date, Bill.type)
            .order_by(Bill.bill_date)
        )
        rows = result.all()

        # 整理为 {date: {income, expense}} 结构
        daily_map: dict[str, dict] = {}
        for bill_date, bill_type, amount in rows:
            d_str = str(bill_date)
            if d_str not in daily_map:
                daily_map[d_str] = {"income": 0.0, "expense": 0.0}
            daily_map[d_str][bill_type] = round(float(amount), 2)

        if include_all_days:
            # 补全范围内所有日期
            daily_data = []
            current = start
            while current <= end:
                d_str = str(current)
                data = daily_map.get(d_str, {"income": 0.0, "expense": 0.0})
                daily_data.append({
                    "date": d_str,
                    "income": data["income"],
                    "expense": data["expense"],
                })
                current += timedelta(days=1)
        else:
            daily_data = [
                {"date": d, "income": v["income"], "expense": v["expense"]}
                for d, v in sorted(daily_map.items())
            ]

        return overview, daily_data

    @staticmethod
    async def _calc_category_pie(
        db: AsyncSession,
        user_id: int,
        start: date,
        end: date,
    ) -> list[dict]:
        """计算支出分类占比（饼图数据）。"""
        result = await db.execute(
            select(
                Category.id,
                Category.name,
                Category.icon,
                Category.color,
                func.coalesce(func.sum(Bill.amount), 0).label("total"),
            )
            .join(Bill, Bill.category_id == Category.id)
            .where(
                Bill.user_id == user_id,
                Bill.type == "expense",
                Bill.bill_date >= start,
                Bill.bill_date <= end,
            )
            .group_by(Category.id, Category.name, Category.icon, Category.color)
            .order_by(func.sum(Bill.amount).desc())
        )
        rows = result.all()

        total_expense = sum(float(r[4]) for r in rows)
        if total_expense == 0:
            return []

        return [
            {
                "category_id": r[0],
                "category_name": r[1],
                "icon": r[2],
                "color": r[3],
                "amount": round(float(r[4]), 2),
                "percentage": round((float(r[4]) / total_expense) * 100, 1),
            }
            for r in rows
        ]

    @staticmethod
    async def _calc_category_ranks(
        db: AsyncSession,
        user_id: int,
        start: date,
        end: date,
        limit: int = 10,
    ) -> list[dict]:
        """计算支出分类排行 Top N（条形图数据）。"""
        result = await db.execute(
            select(
                Category.id,
                Category.name,
                Category.icon,
                Category.color,
                func.coalesce(func.sum(Bill.amount), 0).label("total"),
            )
            .join(Bill, Bill.category_id == Category.id)
            .where(
                Bill.user_id == user_id,
                Bill.type == "expense",
                Bill.bill_date >= start,
                Bill.bill_date <= end,
            )
            .group_by(Category.id, Category.name, Category.icon, Category.color)
            .order_by(func.sum(Bill.amount).desc())
            .limit(limit)
        )
        rows = result.all()

        total_expense = sum(float(r[4]) for r in rows)
        if total_expense == 0:
            return []

        ranks = []
        for rank, r in enumerate(rows, start=1):
            ranks.append({
                "rank": rank,
                "category_id": r[0],
                "category_name": r[1],
                "icon": r[2],
                "color": r[3],
                "amount": round(float(r[4]), 2),
                "percentage": round((float(r[4]) / total_expense) * 100, 1),
            })
        return ranks

    @staticmethod
    async def _calc_calendar_heatmap(
        db: AsyncSession,
        user_id: int,
        start: date,
        end: date,
    ) -> list[dict]:
        """计算消费日历热力图数据。"""
        # 查询每日支出
        result = await db.execute(
            select(
                Bill.bill_date,
                func.coalesce(func.sum(Bill.amount), 0).label("total"),
            )
            .where(
                Bill.user_id == user_id,
                Bill.type == "expense",
                Bill.bill_date >= start,
                Bill.bill_date <= end,
            )
            .group_by(Bill.bill_date)
        )
        rows = result.all()

        day_amounts = {r[0]: float(r[1]) for r in rows}
        max_amount = max(day_amounts.values()) if day_amounts else 1.0

        calendar_data = []
        current = start
        while current <= end:
            amount = day_amounts.get(current, 0.0)
            calendar_data.append({
                "date": str(current),
                "day_of_month": current.day,
                "day_of_week": current.weekday(),  # 0=Monday
                "amount": round(amount, 2),
                "intensity": round(amount / max_amount, 2) if max_amount > 0 else 0.0,
            })
            current += timedelta(days=1)

        return calendar_data

    @staticmethod
    def _calc_comparison(current: dict, prev: dict) -> dict | None:
        """计算环比变化百分比。"""
        if prev["total_income"] == 0 and prev["total_expense"] == 0:
            return None

        def _pct(cur, prev_val):
            if prev_val == 0:
                return 100.0 if cur > 0 else 0.0
            return round(((cur - prev_val) / prev_val) * 100, 1)

        return {
            "prev_income": prev["total_income"],
            "prev_expense": prev["total_expense"],
            "income_change_pct": _pct(current["total_income"], prev["total_income"]),
            "expense_change_pct": _pct(current["total_expense"], prev["total_expense"]),
        }
