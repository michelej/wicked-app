from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ImportedTransactionBase(BaseModel):
    source_bank: str = Field(..., pattern="^(bbva|ing_direct)$")
    source_file_name: str = Field(..., min_length=1, max_length=255)
    source_row_number: int = Field(..., ge=1)
    fingerprint: str = Field(..., min_length=1, max_length=64)
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: Optional[str] = Field(default="EUR", max_length=10)
    value_date: Optional[datetime] = None
    booking_date: Optional[datetime] = None
    suggested_timestamp: Optional[datetime] = None
    raw_concept: Optional[str] = Field(default=None, max_length=500)
    raw_movement: Optional[str] = Field(default=None, max_length=255)
    raw_observations: Optional[str] = Field(default=None, max_length=1000)
    comment_suggestion: Optional[str] = Field(default=None, max_length=1000)
    payment_method_suggestion: Optional[str] = Field(default=None, pattern="^(cash|credit|debit)$")
    available_balance: Optional[Decimal] = Field(default=None, decimal_places=2)
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending", pattern="^(pending|processed_imported|processed_skipped)$")
    processed_transaction_id: Optional[str] = None
    processed_budget_id: Optional[str] = None
    processed_category: Optional[str] = Field(default=None, max_length=100)
    processed_bank: Optional[str] = Field(default=None, max_length=100)
    processed_payment_method: Optional[str] = Field(default=None, pattern="^(cash|credit|debit)$")
    processed_comment: Optional[str] = Field(default=None, max_length=1000)
    processed_timestamp: Optional[datetime] = None
    processed_is_charged: Optional[bool] = None
    processed_at: Optional[datetime] = None


class ImportedTransaction(ImportedTransactionBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            Decimal: lambda value: float(value)
        }


class ImportedTransactionProcess(BaseModel):
    import_to_system: bool = True
    budget_id: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bank: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, pattern="^(cash|credit|debit)$")
    comment: Optional[str] = Field(default=None, max_length=1000)
    timestamp: Optional[datetime] = None
    is_charged: bool = False
    type: Optional[str] = Field(default=None, pattern="^(income|expense)$")


class ImportedTransactionsUploadResponse(BaseModel):
    source_bank: str = Field(..., pattern="^(bbva|ing_direct)$")
    file_name: str
    total_rows: int = Field(..., ge=0)
    imported_count: int = Field(..., ge=0)
    duplicate_count: int = Field(..., ge=0)
    pending_count: int = Field(..., ge=0)
    preview: list[ImportedTransaction] = Field(default_factory=list)
