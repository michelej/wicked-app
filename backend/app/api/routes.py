from fastapi import APIRouter
from app.api.endpoints import (
    categories,
    budgets,
    transactions,
    templates,
    recurring_expenses,
    dashboard
)

router = APIRouter()

# Include all endpoint routers
router.include_router(categories.router)
router.include_router(budgets.router)
router.include_router(transactions.router)
router.include_router(templates.router)
router.include_router(recurring_expenses.router)
router.include_router(dashboard.router)
