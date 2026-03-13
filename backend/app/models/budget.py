from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class BudgetItem(BaseModel):
    """Individual budget item for a specific category"""
    category: str = Field(..., min_length=1, max_length=100)
    planned_amount: Decimal = Field(..., gt=0, decimal_places=2)
    spent_amount: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime
    budget_items: List[BudgetItem] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|closed|draft)$")
    created_from_template: Optional[str] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_items: Optional[List[BudgetItem]] = None
    status: Optional[str] = Field(None, pattern="^(active|closed|draft)$")


class Budget(BudgetBase):
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
                "name": "Marzo 2026",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "budget_items": [
                    {"category": "Comida", "planned_amount": 500.0, "spent_amount": 150.0},
                    {"category": "Gasolina", "planned_amount": 250.0, "spent_amount": 0.0},
                    {"category": "Netflix", "planned_amount": 15.99, "spent_amount": 15.99}
                ],
                "status": "active",
                "created_from_template": None,
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00"
            }
        }


class BudgetSummary(BaseModel):
    budget_id: str
    total_planned: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    balance: Decimal  # income - expenses (old calculation for compatibility)
    charged_balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    charged_income: Decimal
    charged_expense: Decimal
    pending_income: Decimal
    pending_expense: Decimal
    transactions_count: int
    budget_items: List[BudgetItem] = Field(default_factory=list)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
