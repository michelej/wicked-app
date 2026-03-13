from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.core.database import get_database
from app.models.template import BudgetTemplate, TemplateCreate, TemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", response_model=BudgetTemplate, status_code=201)
async def create_template(
    template: TemplateCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new budget template"""
    service = TemplateService(db)
    return await service.create_template(template)


@router.get("", response_model=List[BudgetTemplate])
async def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all templates"""
    service = TemplateService(db)
    return await service.get_templates(skip, limit)


@router.get("/{template_id}", response_model=BudgetTemplate)
async def get_template(
    template_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific template by ID"""
    service = TemplateService(db)
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=BudgetTemplate)
async def update_template(
    template_id: str,
    template_update: TemplateUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a template"""
    service = TemplateService(db)
    template = await service.update_template(template_id, template_update)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a template"""
    service = TemplateService(db)
    
    # Check if template exists
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    success = await service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete template")
