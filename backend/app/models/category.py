from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(income|expense|both)$")
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    parent_id: Optional[str] = Field(None, description="Parent category ID for subcategories")
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(income|expense|both)$")
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    parent_id: Optional[str] = Field(None, description="Parent category ID for subcategories")
    is_active: Optional[bool] = None


class Category(CategoryBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Agua",
                "type": "expense",
                "icon": "pi pi-tint",
                "color": "#3B82F6",
                "parent_id": "507f1f77bcf86cd799439010",
                "is_active": True,
                "created_at": "2026-03-02T10:00:00",
                "updated_at": "2026-03-02T10:00:00"
            }
        }
