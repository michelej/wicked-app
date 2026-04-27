from fastapi import APIRouter, Depends, HTTPException, Query, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_database
from app.models.recurring_expense import RecurringExpense, RecurringExpenseCreate, RecurringExpenseUpdate
from app.models.transaction import Transaction
from app.models.budget import Budget, BudgetUpdate, BudgetItem
from app.services.recurring_service import RecurringExpenseService
from app.services.transaction_service import TransactionService
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])


class ApplyRecurringRequest(BaseModel):
    budget_id: str
    recurring_expense_ids: List[str]


@router.post("", response_model=RecurringExpense, status_code=201)
async def create_recurring_expense(
    expense: RecurringExpenseCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new recurring expense"""
    service = RecurringExpenseService(db)
    try:
        return await service.create_recurring_expense(expense)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=List[RecurringExpense])
async def get_recurring_expenses(
    is_active: Optional[bool] = None,
    frequency: Optional[str] = Query(None, pattern="^(monthly|annual|quarterly)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all recurring expenses with optional filters"""
    service = RecurringExpenseService(db)
    return await service.get_recurring_expenses(is_active, frequency, skip, limit)


@router.get("/active", response_model=List[RecurringExpense])
async def get_active_recurring_expenses(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all active recurring expenses"""
    service = RecurringExpenseService(db)
    return await service.get_active_recurring_expenses()


@router.get("/{expense_id}", response_model=RecurringExpense)
async def get_recurring_expense(
    expense_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific recurring expense by ID"""
    service = RecurringExpenseService(db)
    expense = await service.get_recurring_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return expense


@router.put("/{expense_id}", response_model=RecurringExpense)
async def update_recurring_expense(
    expense_id: str,
    expense_update: RecurringExpenseUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a recurring expense"""
    service = RecurringExpenseService(db)
    try:
        expense = await service.update_recurring_expense(expense_id, expense_update)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not expense:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    return expense


@router.delete("/{expense_id}", status_code=204)
async def delete_recurring_expense(
    expense_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a recurring expense"""
    service = RecurringExpenseService(db)
    
    # Check if expense exists
    expense = await service.get_recurring_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    
    success = await service.delete_recurring_expense(expense_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete recurring expense")


@router.post("/apply-to-budget", response_model=Budget, status_code=200)
async def apply_recurring_to_budget(
    request: ApplyRecurringRequest = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Apply selected recurring expenses to a budget by adding budget items (planned amounts)"""
    recurring_service = RecurringExpenseService(db)
    budget_service = BudgetService(db)
    
    # Verify budget exists
    budget = await budget_service.get_budget(request.budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Get recurring expenses
    recurring_expenses = []
    for expense_id in request.recurring_expense_ids:
        expense = await recurring_service.get_recurring_expense(expense_id)
        if expense:
            recurring_expenses.append(expense)
    
    if not recurring_expenses:
        raise HTTPException(status_code=400, detail="No valid recurring expenses found")
    
    # Update budget_items with recurring expense categories and amounts
    existing_items = budget.budget_items if budget.budget_items else []
    items_dict = {}
    
    # Convert existing items to dict with planned_amount as float
    for item in existing_items:
        item_key = item.category_id or item.category
        if not item_key:
            continue

        items_dict[item_key] = {
            'category_id': item.category_id,
            'category': item.category,
            'planned_amount': float(item.planned_amount),
            'spent_amount': float(item.spent_amount)
        }
    
    # Add or update budget items for each recurring expense
    for expense in recurring_expenses:
        expense_key = expense.category_id or expense.category
        if not expense_key:
            continue

        if expense_key in items_dict:
            # Category already exists, add the amount to planned_amount
            items_dict[expense_key]['planned_amount'] += float(expense.amount)
        else:
            # Create new budget item
            items_dict[expense_key] = {
                'category_id': expense.category_id,
                'category': expense.category,
                'planned_amount': float(expense.amount),
                'spent_amount': 0
            }
    
    # Convert dict back to BudgetItem list
    updated_items = [
        BudgetItem(
            category_id=item.get('category_id'),
            category=item.get('category'),
            planned_amount=item['planned_amount'],
            spent_amount=item['spent_amount']
        )
        for item in items_dict.values()
    ]
    
    # Update budget with new budget_items
    updated_budget = await budget_service.update_budget(
        request.budget_id,
        BudgetUpdate(budget_items=updated_items)
    )
    
    return updated_budget
