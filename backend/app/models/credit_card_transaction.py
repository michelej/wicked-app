from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreditCardTransactionBase(BaseModel):
    budget_id: str = Field(..., min_length=1)
    credit_card: str = Field(..., min_length=1, max_length=100)
    type: Literal["income", "expense"]
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=100)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: Literal["credit"] = "credit"
    comment: Optional[str] = Field(None, max_length=500)
    timestamp: datetime
    is_charged: bool = False


class CreditCardTransactionCreate(CreditCardTransactionBase):
    pass


class CreditCardTransactionUpdate(BaseModel):
    budget_id: Optional[str] = Field(None, min_length=1)
    credit_card: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[Literal["income", "expense"]] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[Literal["credit"]] = None
    comment: Optional[str] = Field(None, max_length=500)
    timestamp: Optional[datetime] = None
    is_charged: Optional[bool] = None


class CreditCardTransaction(CreditCardTransactionBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {Decimal: lambda v: float(v)}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "budget_id": "507f1f77bcf86cd799439012",
                "credit_card": "ING Direct",
                "type": "expense",
                "amount": 89.99,
                "category": "Supermercado",
                "bank": "ING Direct",
                "payment_method": "credit",
                "comment": "Compra semanal",
                "timestamp": "2026-03-01T10:00:00",
                "is_charged": False,
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00"
            }
        }
