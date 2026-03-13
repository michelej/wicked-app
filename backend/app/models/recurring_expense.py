from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class RecurringExpenseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: str = Field(..., pattern="^(cash|credit|debit)$")
    frequency: str = Field(..., pattern="^(monthly|annual|quarterly|one-time)$")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    specific_date: Optional[date] = None  # For one-time expenses
    comment: Optional[str] = Field(None, max_length=500)
    is_active: bool = True

    @field_validator('day_of_month')
    @classmethod
    def validate_day_of_month(cls, v, info):
        frequency = info.data.get('frequency')
        if frequency in ['monthly', 'annual', 'quarterly'] and v is None:
            raise ValueError('day_of_month is required for monthly, annual, and quarterly frequencies')
        return v
    
    @field_validator('specific_date')
    @classmethod
    def validate_specific_date(cls, v, info):
        frequency = info.data.get('frequency')
        if frequency == 'one-time' and v is None:
            raise ValueError('specific_date is required for one-time frequency')
        return v


class RecurringExpenseCreate(RecurringExpenseBase):
    pass


class RecurringExpenseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, pattern="^(cash|credit|debit)$")
    frequency: Optional[str] = Field(None, pattern="^(monthly|annual|quarterly|one-time)$")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    specific_date: Optional[date] = None
    comment: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class RecurringExpense(RecurringExpenseBase):
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
                "name": "Netflix Premium",
                "category": "Netflix",
                "amount": 12.99,
                "bank": "Banco Santander",
                "payment_method": "credit",
                "frequency": "monthly",
                "day_of_month": 5,
                "specific_date": None,
                "comment": "Subscripción mensual",
                "is_active": True,
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00"
            }
        }
