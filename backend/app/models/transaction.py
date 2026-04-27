from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    budget_id: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category_id: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: str = Field(..., pattern="^(cash|credit|debit)$")
    comment: Optional[str] = Field(None, max_length=500)
    timestamp: datetime
    is_charged: bool = False

    @model_validator(mode="after")
    def validate_category_reference(self):
        if self.category_id or self.category:
            return self

        raise ValueError("category_id or category is required")


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    budget_id: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, pattern="^(cash|credit|debit)$")
    comment: Optional[str] = Field(None, max_length=500)
    timestamp: Optional[datetime] = None
    is_charged: Optional[bool] = None


class Transaction(TransactionBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "budget_id": "507f1f77bcf86cd799439012",
                "type": "expense",
                "amount": 12.99,
                "category_id": "507f1f77bcf86cd799439099",
                "category": "Netflix",
                "bank": "Banco Santander",
                "payment_method": "credit",
                "comment": "Subscripción mensual",
                "timestamp": "2026-03-01T10:00:00",
                "is_charged": True,
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00"
            }
        }
