from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=Transaction, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new transaction"""
    service = TransactionService(db)
    try:
        return await service.create_transaction(transaction)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=List[Transaction])
async def get_transactions(
    budget_id: Optional[str] = None,
    type_filter: Optional[str] = Query(None, pattern="^(income|expense)$"),
    category: Optional[str] = None,
    category_id: Optional[str] = None,
    is_charged: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all transactions with optional filters"""
    service = TransactionService(db)
    return await service.get_transactions(
        budget_id, type_filter, category, category_id, is_charged,
        start_date, end_date, skip, limit
    )


@router.get("/budget/{budget_id}", response_model=List[Transaction])
async def get_transactions_by_budget(
    budget_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all transactions for a specific budget"""
    service = TransactionService(db)
    return await service.get_transactions_by_budget(budget_id)


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific transaction by ID"""
    service = TransactionService(db)
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a transaction"""
    service = TransactionService(db)
    try:
        transaction = await service.update_transaction(transaction_id, transaction_update)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}/charge", response_model=Transaction)
async def mark_transaction_charged(
    transaction_id: str,
    is_charged: bool = Query(True, description="Mark as charged (true) or uncharged (false)"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark a transaction as charged or uncharged"""
    service = TransactionService(db)
    transaction = await service.mark_as_charged(transaction_id, is_charged)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a transaction"""
    service = TransactionService(db)
    
    # Check if transaction exists
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    success = await service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete transaction")


@router.post("/bulk", response_model=List[Transaction], status_code=201)
async def bulk_create_transactions(
    transactions: List[TransactionCreate],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create multiple transactions at once"""
    service = TransactionService(db)
    try:
        return await service.bulk_create_transactions(transactions)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
