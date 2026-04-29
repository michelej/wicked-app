from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.registry_item import RegistryItem, RegistryItemCreate, RegistryItemUpdate
from app.services.registry_service import RegistryService


router = APIRouter(prefix="/registry-items", tags=["registry"])


@router.post("", response_model=RegistryItem, status_code=status.HTTP_201_CREATED)
async def create_registry_item(
    item: RegistryItemCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    return await service.create_item(item)


@router.get("", response_model=List[RegistryItem])
async def get_registry_items(
    type_filter: Optional[str] = Query(default=None, alias="type"),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    tags: Optional[List[str]] = Query(default=None),
    search: Optional[str] = None,
    start_date: Optional[datetime] = Query(default=None, alias="startDate"),
    end_date: Optional[datetime] = Query(default=None, alias="endDate"),
    min_amount: Optional[float] = Query(default=None, alias="minAmount", ge=0),
    max_amount: Optional[float] = Query(default=None, alias="maxAmount", ge=0),
    location: Optional[str] = None,
    related_entity_type: Optional[str] = Query(default=None, alias="relatedEntityType"),
    related_entity_id: Optional[str] = Query(default=None, alias="relatedEntityId"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    return await service.get_items(
        type_filter=type_filter,
        status=status_filter,
        tags=tags,
        search=search,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        location=location,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{item_id}", response_model=RegistryItem)
async def get_registry_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registry item not found")
    return item


@router.put("/{item_id}", response_model=RegistryItem)
async def update_registry_item(
    item_id: str,
    item_update: RegistryItemUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    item = await service.update_item(item_id, item_update)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registry item not found")
    return item


@router.post("/{item_id}/archive", response_model=RegistryItem)
async def archive_registry_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    item = await service.archive_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registry item not found")
    return item


@router.post("/{item_id}/duplicate", response_model=RegistryItem, status_code=status.HTTP_201_CREATED)
async def duplicate_registry_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    item = await service.duplicate_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registry item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registry_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = RegistryService(db)
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registry item not found")
