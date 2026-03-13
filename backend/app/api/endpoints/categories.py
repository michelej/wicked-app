from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from app.core.database import get_database
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=Category, status_code=201)
async def create_category(
    category: CategoryCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new category"""
    service = CategoryService(db)
    return await service.create_category(category)


@router.get("", response_model=List[Category])
async def get_categories(
    type_filter: Optional[str] = Query(None, pattern="^(income|expense|both)$"),
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all categories with optional filters"""
    service = CategoryService(db)
    return await service.get_categories(type_filter, is_active, skip, limit)


@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific category by ID"""
    service = CategoryService(db)
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a category"""
    service = CategoryService(db)
    category = await service.update_category(category_id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    force: bool = Query(False, description="Force delete even if in use"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a category"""
    service = CategoryService(db)
    
    # Check if category exists
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has subcategories
    has_subcategories = await service.has_subcategories(category_id)
    if has_subcategories and not force:
        raise HTTPException(
            status_code=400, 
            detail="Category has subcategories. Delete them first or use force=true."
        )
    
    # Check if category is in use
    if not force:
        in_use = await service.is_category_in_use(category.name)
        if in_use:
            raise HTTPException(
                status_code=400, 
                detail="Category is in use. Use force=true to delete anyway."
            )
    
    success = await service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete category")


@router.get("/parent/list", response_model=List[Category])
async def get_parent_categories(
    type_filter: Optional[str] = Query(None, pattern="^(income|expense|both)$"),
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get only parent categories (categories without parent_id)"""
    service = CategoryService(db)
    return await service.get_parent_categories(type_filter, is_active)


@router.get("/{category_id}/subcategories", response_model=List[Category])
async def get_subcategories(
    category_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all subcategories of a parent category"""
    service = CategoryService(db)
    
    # Check if parent category exists
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Parent category not found")
    
    return await service.get_subcategories(category_id)
