from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


RegistryItemType = Literal[
    "date",
    "trip",
    "purchase",
    "warranty",
    "document",
    "event",
    "note",
    "subscription",
    "task",
    "procedure",
    "other",
]

RegistryItemStatus = Literal[
    "active",
    "planned",
    "completed",
    "cancelled",
    "archived",
]

CustomFieldType = Literal["text", "number", "date", "boolean", "url", "select", "currency"]
RelatedEntityType = Literal["transaction", "budget", "document", "contact", "project", "category"]


class RelatedEntity(BaseModel):
    entityType: RelatedEntityType
    entityId: str = Field(..., min_length=1, max_length=120)
    label: Optional[str] = Field(default=None, max_length=120)


class CustomField(BaseModel):
    key: str = Field(..., min_length=1, max_length=80)
    label: str = Field(..., min_length=1, max_length=120)
    type: CustomFieldType
    value: Any = None


class Attachment(BaseModel):
    label: str = Field(..., min_length=1, max_length=120)
    url: str = Field(..., min_length=1, max_length=500)
    kind: Optional[str] = Field(default=None, max_length=50)


class RegistryItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=4000)
    type: RegistryItemType
    status: RegistryItemStatus = "active"
    date: Optional[datetime] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=1, max_length=8)
    location: Optional[str] = Field(default=None, max_length=200)
    tags: List[str] = Field(default_factory=list)
    relatedEntities: List[RelatedEntity] = Field(default_factory=list)
    customFields: List[CustomField] = Field(default_factory=list)
    attachments: List[Attachment] = Field(default_factory=list)


class RegistryItemCreate(RegistryItemBase):
    pass


class RegistryItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=4000)
    type: Optional[RegistryItemType] = None
    status: Optional[RegistryItemStatus] = None
    date: Optional[datetime] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=1, max_length=8)
    location: Optional[str] = Field(default=None, max_length=200)
    tags: Optional[List[str]] = None
    relatedEntities: Optional[List[RelatedEntity]] = None
    customFields: Optional[List[CustomField]] = None
    attachments: Optional[List[Attachment]] = None


class RegistryItem(RegistryItemBase):
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "registry_123",
                "title": "Viaje a Suecia",
                "description": "Reserva inicial con notas y presupuesto.",
                "type": "trip",
                "status": "planned",
                "startDate": "2026-07-08T00:00:00",
                "endDate": "2026-07-14T00:00:00",
                "tags": ["familia", "verano"],
                "relatedEntities": [{"entityType": "budget", "entityId": "budget_1", "label": "Verano 2026"}],
                "customFields": [{"key": "hotel", "label": "Hotel", "type": "text", "value": "Stockholm Stay"}],
                "attachments": [{"label": "Reserva", "url": "https://example.com/reserva.pdf", "kind": "document"}],
                "createdAt": "2026-04-20T10:00:00",
                "updatedAt": "2026-04-20T10:00:00",
            }
        }
