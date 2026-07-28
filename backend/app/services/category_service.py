"""
分类业务逻辑层 — 分类 CRUD + 默认分类初始化。
"""
import logging
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.bill import Bill
from app.models.user import User
from app.exceptions import NotFoundError, ConflictError, ForbiddenError, ValidationError

logger = logging.getLogger("dailytracker.category")


class CategoryService:
    """分类服务 — 管理系统默认分类和用户自定义分类。"""

    # ============================================================
    # 默认分类数据 — 与 init.sql 保持一致
    # ============================================================
    DEFAULT_CATEGORIES = [
        # 支出 (8个)
        {"name": "餐饮", "icon": "🍽️", "color": "#E07B5A", "type": "expense", "sort_order": 1},
        {"name": "交通", "icon": "🚗", "color": "#C0826B", "type": "expense", "sort_order": 2},
        {"name": "购物", "icon": "🛒", "color": "#D4956B", "type": "expense", "sort_order": 3},
        {"name": "居住", "icon": "🏠", "color": "#B8846E", "type": "expense", "sort_order": 4},
        {"name": "娱乐", "icon": "🎮", "color": "#D4A574", "type": "expense", "sort_order": 5},
        {"name": "医疗", "icon": "💊", "color": "#E8916B", "type": "expense", "sort_order": 6},
        {"name": "教育", "icon": "📚", "color": "#C0956E", "type": "expense", "sort_order": 7},
        {"name": "其他支出", "icon": "📌", "color": "#B0A090", "type": "expense", "sort_order": 8},
        # 收入 (5个)
        {"name": "工资", "icon": "💰", "color": "#7BA587", "type": "income", "sort_order": 1},
        {"name": "兼职", "icon": "💼", "color": "#6B9EB3", "type": "income", "sort_order": 2},
        {"name": "投资", "icon": "📈", "color": "#8B8BA7", "type": "income", "sort_order": 3},
        {"name": "红包", "icon": "🧧", "color": "#C49B7A", "type": "income", "sort_order": 4},
        {"name": "其他收入", "icon": "📌", "color": "#B0A090", "type": "income", "sort_order": 5},
    ]

    @classmethod
    async def ensure_default_categories(cls, db: AsyncSession):
        """
        确保默认分类数据已插入。
        在应用首次启动或数据库为空时调用。
        """
        result = await db.execute(
            select(func.count(Category.id)).where(Category.is_default == True)
        )
        count = result.scalar()
        if count == 0:
            for cat_data in cls.DEFAULT_CATEGORIES:
                cat = Category(
                    user_id=None,
                    name=cat_data["name"],
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    type=cat_data["type"],
                    is_default=True,
                    sort_order=cat_data["sort_order"],
                )
                db.add(cat)
            logger.info("默认分类数据已初始化")
        else:
            logger.info(f"默认分类已存在 ({count} 条)")

    # ============================================================
    # CRUD
    # ============================================================
    @staticmethod
    async def get_categories(
        db: AsyncSession,
        user_id: int,
        type_filter: str | None = None,
    ) -> list[dict]:
        """
        获取分类列表 — 系统默认 + 用户自定义。

        排序规则：
        1. 系统默认分类按 sort_order 排序
        2. 用户自定义分类按创建时间排序
        3. 有账单记录的排在前面
        """
        # 查询条件：系统默认 或 属于该用户
        conditions = (Category.is_default == True) | (Category.user_id == user_id)
        if type_filter:
            conditions = conditions & (Category.type == type_filter)

        query = (
            select(Category)
            .where(conditions)
            .order_by(
                # 系统默认优先
                case((Category.is_default == True, 0), else_=1),
                Category.sort_order,
                Category.created_at,
            )
        )
        result = await db.execute(query)
        categories = result.scalars().all()

        # 统计每个分类的账单数量
        output = []
        for cat in categories:
            bill_count_result = await db.execute(
                select(func.count(Bill.id)).where(
                    Bill.category_id == cat.id,
                    Bill.user_id == user_id,
                )
            )
            bill_count = bill_count_result.scalar() or 0
            output.append({
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "type": cat.type,
                "is_default": cat.is_default,
                "sort_order": cat.sort_order,
                "bill_count": bill_count,
            })

        return output

    @staticmethod
    async def create_category(
        db: AsyncSession,
        user_id: int,
        name: str,
        icon: str,
        color: str,
        cat_type: str,
        sort_order: int = 0,
    ) -> dict:
        """创建用户自定义分类。"""
        # 检查同名分类
        existing = await db.execute(
            select(Category).where(
                Category.name == name,
                (Category.user_id == user_id) | (Category.is_default == True),
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"分类 '{name}' 已存在")

        category = Category(
            user_id=user_id,
            name=name,
            icon=icon,
            color=color,
            type=cat_type,
            is_default=False,
            sort_order=sort_order,
        )
        db.add(category)
        await db.flush()
        await db.refresh(category)

        logger.info(f"自定义分类创建成功: {category.name} (user={user_id})")

        return {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "color": category.color,
            "type": category.type,
            "is_default": category.is_default,
            "sort_order": category.sort_order,
            "bill_count": 0,
        }

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category_id: int,
        user_id: int,
        **kwargs,
    ) -> dict:
        """编辑分类。"""
        category = await CategoryService._get_editable_category(db, category_id, user_id)

        for field, value in kwargs.items():
            if value is not None:
                setattr(category, field, value)

        await db.flush()
        await db.refresh(category)

        return {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "color": category.color,
            "type": category.type,
            "is_default": category.is_default,
            "sort_order": category.sort_order,
            "bill_count": 0,
        }

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> None:
        """
        删除分类。

        规则：
        - 系统默认分类不可删除
        - 有账单关联的分类不可删除
        """
        category = await CategoryService._get_editable_category(db, category_id, user_id)

        # 默认分类不可删除
        if category.is_default:
            raise ForbiddenError("系统默认分类不可删除")

        # 检查是否有关联账单
        bill_count_result = await db.execute(
            select(func.count(Bill.id)).where(Bill.category_id == category_id)
        )
        bill_count = bill_count_result.scalar() or 0
        if bill_count > 0:
            raise ConflictError(f"该分类下有 {bill_count} 笔账单，无法删除")

        await db.delete(category)
        await db.flush()

        logger.info(f"分类已删除: {category.name} (id={category_id})")

    # ============================================================
    # 内部方法
    # ============================================================
    @staticmethod
    async def _get_editable_category(db: AsyncSession, category_id: int, user_id: int) -> Category:
        """获取可编辑的分类（用户自己的自定义分类 或 系统默认分类）。"""
        result = await db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if category is None:
            raise NotFoundError("分类不存在")

        # 系统默认分类可以被编辑（但不能删除）
        if not category.is_default and category.user_id != user_id:
            raise ForbiddenError("无权操作此分类")

        return category
