from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from datetime import datetime
from app.core.database import get_database
from app.services.dashboard_service import DashboardService
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/daily-progress/{budget_id}", response_model=List[Dict[str, Any]])
async def get_daily_progress(
    budget_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get day-by-day financial progress for a budget"""
    budget_service = BudgetService(db)
    dashboard_service = DashboardService(db)
    
    # Verify budget exists
    budget = await budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return await dashboard_service.get_daily_progress(
        budget_id,
        budget.start_date,
        budget.end_date
    )


@router.get("/category-summary/{budget_id}", response_model=List[Dict[str, Any]])
async def get_category_summary(
    budget_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get expense summary grouped by category"""
    budget_service = BudgetService(db)
    dashboard_service = DashboardService(db)
    
    # Verify budget exists
    budget = await budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return await dashboard_service.get_category_summary(budget_id)


@router.get("/payment-method-summary/{budget_id}", response_model=List[Dict[str, Any]])
async def get_payment_method_summary(
    budget_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get summary grouped by payment method"""
    budget_service = BudgetService(db)
    dashboard_service = DashboardService(db)
    
    # Verify budget exists
    budget = await budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return await dashboard_service.get_payment_method_summary(budget_id)


@router.get("/upcoming-expenses", response_model=List[Dict[str, Any]])
async def get_upcoming_expenses(
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get upcoming recurring expenses"""
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_upcoming_recurring_expenses(days_ahead)


@router.get("/budget-comparison", response_model=List[Dict[str, Any]])
async def get_budget_comparison(
    budget_ids: List[str] = Query(..., description="List of budget IDs to compare"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Compare financial summaries across multiple budgets"""
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_budget_comparison(budget_ids)
