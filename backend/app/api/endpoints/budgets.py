from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from app.core.database import get_database
from app.models.budget import Budget, BudgetCreate, BudgetUpdate, BudgetSummary, MonthlyBudgetSummary
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=Budget, status_code=201)
async def create_budget(
    budget: BudgetCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new budget"""
    service = BudgetService(db)
    
    # Validate dates
    if budget.start_date >= budget.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    return await service.create_budget(budget)


@router.get("", response_model=List[Budget])
async def get_budgets(
    status: Optional[str] = Query(None, pattern="^(active|closed|draft)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all budgets with optional filters"""
    service = BudgetService(db)
    return await service.get_budgets(status, skip, limit)


@router.get("/active", response_model=List[Budget])
async def get_active_budgets(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all active budgets"""
    service = BudgetService(db)
    return await service.get_active_budgets()


@router.get("/monthly-summary", response_model=List[MonthlyBudgetSummary])
async def get_monthly_budget_summary(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get monthly budget summaries grouped by budget_month"""
    service = BudgetService(db)
    return await service.get_monthly_budget_summary()


@router.get("/{budget_id}/summary", response_model=BudgetSummary)
async def get_budget_summary(
    budget_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get financial summary for a budget"""
    service = BudgetService(db)
    
    # Check if budget exists
    budget = await service.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    summary = await service.get_budget_summary(budget_id)
    if not summary:
        raise HTTPException(status_code=500, detail="Failed to generate summary")
    
    return summary


@router.put("/{budget_id}", response_model=Budget)
async def update_budget(
    budget_id: str,
    budget_update: BudgetUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a specific budget"""
    service = BudgetService(db)
    
    # Check if budget exists
    budget = await service.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Validate dates if both are provided
    start_date = budget_update.start_date or budget.start_date
    end_date = budget_update.end_date or budget.end_date
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    return await service.update_budget(budget_id, budget_update)


@router.get("/{budget_id}", response_model=Budget)
async def get_budget(
    budget_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific budget by ID"""
    service = BudgetService(db)
    budget = await service.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget
