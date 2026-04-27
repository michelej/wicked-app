from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Union, Literal
from datetime import datetime
from decimal import Decimal


BankName = Literal["BBVA", "ING Direct"]


class BudgetItem(BaseModel):
    """Individual budget item for a specific category"""
    category_id: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    planned_amount: Decimal = Field(..., gt=0, decimal_places=2)
    spent_amount: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)

    @model_validator(mode="after")
    def validate_category_reference(self):
        if self.category_id or self.category:
            return self

        raise ValueError("category_id or category is required")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PlanningTemporaryIncome(BaseModel):
    label: str = Field(..., min_length=1, max_length=120)
    amount: Decimal = Field(..., gt=0, decimal_places=2)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class BudgetPlanningMetadata(BaseModel):
    planner_type: Optional[str] = Field(default=None, max_length=50)
    counterpart_bank: Optional[BankName] = None
    temporary_incomes: List[PlanningTemporaryIncome] = Field(default_factory=list)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime
    budget_month: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Za-z]+-\d{4}$")
    budget_items: List[BudgetItem] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|closed|draft)$")
    created_from_template: Optional[str] = None
    planning_metadata: Optional[BudgetPlanningMetadata] = None


class BudgetCreate(BudgetBase):
    bank: BankName


class Budget(BudgetBase):
    id: str = Field(..., alias="_id")
    bank: Optional[BankName] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bank: Optional[BankName] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_month: Optional[str] = Field(None, min_length=1, max_length=20, pattern=r"^[A-Za-z]+-\d{4}$")
    budget_items: Optional[List[BudgetItem]] = None
    status: Optional[str] = Field(None, pattern="^(active|closed|draft)$")
    planning_metadata: Optional[BudgetPlanningMetadata] = None


class MonthlyBudgetSummary(BaseModel):
    """Summary of budgets grouped by month"""
    budget_month: str
    total_planned: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    total_spent: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    budget_count: int = Field(default=0, ge=0)
    categories_summary: Dict[str, Dict[str, Union[float, int]]] = Field(default_factory=dict)  # category -> {planned, spent, transactions}
    credit_card_total_spent: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    credit_card_transactions_count: int = Field(default=0, ge=0)
    credit_card_categories_summary: Dict[str, Dict[str, Union[float, int]]] = Field(default_factory=dict)  # category -> {planned, spent, transactions}
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
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
