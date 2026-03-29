from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.imported_transaction import (
    ImportedTransaction,
    ImportedTransactionProcess,
    ImportedTransactionsUploadResponse,
)
from app.services.imported_transaction_service import ImportedTransactionService


router = APIRouter(prefix="/imported-transactions", tags=["imported-transactions"])


@router.post("/upload", response_model=ImportedTransactionsUploadResponse, status_code=201)
async def upload_imported_transactions(
    source_bank: str = Form(..., pattern="^(bbva|ing_direct)$"),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Upload and parse an Excel file from a supported bank."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Debes adjuntar un fichero Excel.")

    if not (file.filename.lower().endswith(".xlsx") or file.filename.lower().endswith(".xls")):
        raise HTTPException(status_code=400, detail="Solo se admiten ficheros Excel .xls o .xlsx.")

    content = await file.read()
    service = ImportedTransactionService(db)

    try:
        return await service.upload_transactions(source_bank, file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=List[ImportedTransaction])
async def get_imported_transactions(
    status: Optional[str] = Query(default=None, pattern="^(pending|processed_imported|processed_skipped)$"),
    source_bank: Optional[str] = Query(default=None, pattern="^(bbva|ing_direct)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List imported transactions pending or already processed."""
    service = ImportedTransactionService(db)
    return await service.get_imported_transactions(status=status, source_bank=source_bank, skip=skip, limit=limit)


@router.get("/{imported_transaction_id}", response_model=ImportedTransaction)
async def get_imported_transaction(
    imported_transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get a single imported transaction."""
    service = ImportedTransactionService(db)
    imported_transaction = await service.get_imported_transaction(imported_transaction_id)
    if not imported_transaction:
        raise HTTPException(status_code=404, detail="Imported transaction not found")
    return imported_transaction


@router.post("/{imported_transaction_id}/process", response_model=ImportedTransaction)
async def process_imported_transaction(
    imported_transaction_id: str,
    payload: ImportedTransactionProcess,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Mark an imported transaction as processed and optionally create a real transaction."""
    service = ImportedTransactionService(db)

    try:
        imported_transaction = await service.process_imported_transaction(imported_transaction_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not imported_transaction:
        raise HTTPException(status_code=404, detail="Imported transaction not found")
    return imported_transaction
