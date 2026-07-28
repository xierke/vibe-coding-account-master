from app.api.auth import router as auth_router
from app.api.bills import router as bills_router
from app.api.categories import router as categories_router
from app.api.reports import router as reports_router
from app.api.budgets import router as budgets_router
from app.api.users import router as users_router

__all__ = [
    "auth_router",
    "bills_router",
    "categories_router",
    "reports_router",
    "budgets_router",
    "users_router",
]
