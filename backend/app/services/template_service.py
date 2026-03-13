from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.models.template import BudgetTemplate, TemplateCreate, TemplateUpdate


class TemplateService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.budget_templates
    
    async def create_template(self, template: TemplateCreate) -> BudgetTemplate:
        """Create a new budget template"""
        template_dict = template.model_dump()
        
        # Convert Decimal amounts to float for MongoDB storage
        for item in template_dict.get("template_items", []):
            item["amount"] = float(item["amount"])
        
        template_dict["created_at"] = datetime.utcnow()
        template_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(template_dict)
        template_dict["_id"] = str(result.inserted_id)
        
        return BudgetTemplate(**template_dict)
    
    async def get_template(self, template_id: str) -> Optional[BudgetTemplate]:
        """Get a template by ID"""
        template = await self.collection.find_one({"_id": ObjectId(template_id)})
        if template:
            template["_id"] = str(template["_id"])
            return BudgetTemplate(**template)
        return None
    
    async def get_templates(self, skip: int = 0, limit: int = 100) -> List[BudgetTemplate]:
        """Get all templates"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("name", 1)
        templates = []
        
        async for template in cursor:
            template["_id"] = str(template["_id"])
            templates.append(BudgetTemplate(**template))
        
        return templates
    
    async def update_template(
        self, 
        template_id: str, 
        template_update: TemplateUpdate
    ) -> Optional[BudgetTemplate]:
        """Update a template"""
        update_data = {k: v for k, v in template_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_template(template_id)
        
        # Convert Decimal amounts to float for MongoDB storage
        if "template_items" in update_data:
            for item in update_data["template_items"]:
                item["amount"] = float(item["amount"])
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(template_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return BudgetTemplate(**result)
        return None
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        result = await self.collection.delete_one({"_id": ObjectId(template_id)})
        return result.deleted_count > 0
