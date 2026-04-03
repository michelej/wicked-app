from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.credit_card_transaction import (
    CreditCardTransaction,
    CreditCardTransactionCreate,
    CreditCardTransactionUpdate,
)
from app.services.credit_card_transaction_service import CreditCardTransactionService

router = APIRouter(prefix="/credit-card-transactions", tags=["credit-card-transactions"])


@router.post("", response_model=CreditCardTransaction, status_code=201)
async def create_credit_card_transaction(
    transaction: CreditCardTransactionCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)
    return await service.create_transaction(transaction)


@router.get("", response_model=List[CreditCardTransaction])
async def get_credit_card_transactions(
    budget_id: Optional[str] = None,
    credit_card: Optional[str] = None,
    type_filter: Optional[str] = Query(None, pattern="^(income|expense)$"),
    category: Optional[str] = None,
    is_charged: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)
    return await service.get_transactions(
        budget_id,
        credit_card,
        type_filter,
        category,
        is_charged,
        start_date,
        end_date,
        skip,
        limit,
    )


@router.get("/{transaction_id}", response_model=CreditCardTransaction)
async def get_credit_card_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Credit card transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=CreditCardTransaction)
async def update_credit_card_transaction(
    transaction_id: str,
    transaction_update: CreditCardTransactionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)
    transaction = await service.update_transaction(transaction_id, transaction_update)
    if not transaction:
        raise HTTPException(status_code=404, detail="Credit card transaction not found")
    return transaction


@router.patch("/{transaction_id}/charge", response_model=CreditCardTransaction)
async def mark_credit_card_transaction_charged(
    transaction_id: str,
    is_charged: bool = Query(True, description="Mark as charged (true) or uncharged (false)"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)
    transaction = await service.mark_as_charged(transaction_id, is_charged)
    if not transaction:
        raise HTTPException(status_code=404, detail="Credit card transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=204)
async def delete_credit_card_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)

    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Credit card transaction not found")

    success = await service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete credit card transaction")


@router.post("/bulk", response_model=List[CreditCardTransaction], status_code=201)
async def bulk_create_credit_card_transactions(
    transactions: List[CreditCardTransactionCreate],
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CreditCardTransactionService(db)
    return await service.bulk_create_transactions(transactions)
