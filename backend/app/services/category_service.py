from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.models.category import Category, CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.categories
    
    async def create_category(self, category: CategoryCreate) -> Category:
        """Create a new category"""
        category_dict = category.model_dump()
        category_dict["created_at"] = datetime.utcnow()
        category_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(category_dict)
        category_dict["_id"] = str(result.inserted_id)
        
        return Category(**category_dict)
    
    async def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID"""
        category = await self.collection.find_one({"_id": ObjectId(category_id)})
        if category:
            category["_id"] = str(category["_id"])
            return Category(**category)
        return None
    
    async def get_categories(
        self, 
        type_filter: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Get all categories with optional filters"""
        query = {}
        if type_filter:
            query["type"] = {"$in": [type_filter, "both"]}
        if is_active is not None:
            query["is_active"] = is_active
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("name", 1)
        categories = []
        
        async for category in cursor:
            category["_id"] = str(category["_id"])
            categories.append(Category(**category))
        
        return categories
    
    async def update_category(self, category_id: str, category_update: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        update_data = {k: v for k, v in category_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_category(category_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(category_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return Category(**result)
        return None
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        result = await self.collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0
    
    async def is_category_in_use(self, category_name: str) -> bool:
        """Check if a category is being used in transactions or recurring expenses"""
        transactions_count = await self.db.transactions.count_documents({"category": category_name})
        recurring_count = await self.db.recurring_expenses.count_documents({"category": category_name})
        return transactions_count > 0 or recurring_count > 0
    
    async def get_parent_categories(
        self, 
        type_filter: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Category]:
        """Get only parent categories (no parent_id)"""
        query = {"parent_id": None}
        if type_filter:
            query["type"] = {"$in": [type_filter, "both"]}
        if is_active is not None:
            query["is_active"] = is_active
        
        cursor = self.collection.find(query).sort("name", 1)
        categories = []
        
        async for category in cursor:
            category["_id"] = str(category["_id"])
            categories.append(Category(**category))
        
        return categories
    
    async def get_subcategories(self, parent_id: str) -> List[Category]:
        """Get all subcategories of a parent category"""
        query = {"parent_id": parent_id}
        cursor = self.collection.find(query).sort("name", 1)
        categories = []
        
        async for category in cursor:
            category["_id"] = str(category["_id"])
            categories.append(Category(**category))
        
        return categories
    
    async def has_subcategories(self, category_id: str) -> bool:
        """Check if a category has subcategories"""
        count = await self.collection.count_documents({"parent_id": category_id})
        return count > 0
