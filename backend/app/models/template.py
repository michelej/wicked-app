from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class TemplateItem(BaseModel):
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=100)
    bank: Optional[str] = Field(None, max_length=100)
    payment_method: str = Field(..., pattern="^(cash|credit|debit)$")
    comment: Optional[str] = Field(None, max_length=500)
    is_recurring: bool = False

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_items: List[TemplateItem] = Field(default_factory=list)


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_items: Optional[List[TemplateItem]] = None


class BudgetTemplate(TemplateBase):
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
                "name": "Plantilla Estándar",
                "description": "Gastos mensuales básicos",
                "template_items": [
                    {
                        "type": "expense",
                        "amount": 12.99,
                        "category": "Netflix",
                        "bank": "Banco Santander",
                        "payment_method": "credit",
                        "comment": "Subscripción mensual",
                        "is_recurring": True
                    }
                ],
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00"
            }
        }
