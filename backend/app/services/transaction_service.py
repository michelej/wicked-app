from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.utils.category_references import enrich_category_reference, load_category_reference_maps, require_category_document, resolve_category_document


class TransactionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.transactions

    async def _serialize_transaction_document(self, transaction: dict) -> Transaction:
        category_maps = await load_category_reference_maps(self.db)
        enriched_transaction = enrich_category_reference({**transaction, "_id": str(transaction["_id"])}, category_maps)
        return Transaction(**enriched_transaction)

    async def _serialize_transaction_documents(self, transactions: List[dict]) -> List[Transaction]:
        category_maps = await load_category_reference_maps(self.db)
        return [
            Transaction(**enrich_category_reference({**transaction, "_id": str(transaction["_id"])}, category_maps))
            for transaction in transactions
        ]

    async def _resolve_category_document(self, category_id: Optional[str], category_name: Optional[str], error_message: str) -> dict:
        category_maps = await load_category_reference_maps(self.db)
        return require_category_document(
            category_maps,
            category_id=category_id,
            category_name=category_name,
            error_message=error_message,
        )

    async def _build_category_query(self, category: Optional[str] = None, category_id: Optional[str] = None) -> Optional[dict]:
        if not category and not category_id:
            return None

        category_maps = await load_category_reference_maps(self.db)
        category_document = resolve_category_document(category_maps, category_id=category_id, category_name=category)

        if category_document:
            return {
                "$or": [
                    {"category_id": category_document["_id"]},
                    {"category": category_document["name"]},
                ]
            }

        if category_id:
            return {"category_id": category_id}

        return {"category": category}
    
    async def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        transaction_dict = transaction.model_dump()
        category_document = await self._resolve_category_document(
            transaction.category_id,
            transaction.category,
            "Category not found for transaction",
        )

        # Convert Decimal to float for MongoDB storage
        transaction_dict["amount"] = float(transaction_dict["amount"])
        transaction_dict["category_id"] = category_document["_id"]
        transaction_dict.pop("category", None)
        transaction_dict["created_at"] = datetime.utcnow()
        transaction_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(transaction_dict)
        transaction_dict["_id"] = str(result.inserted_id)
        
        # Recalculate budget items if it's an expense
        if transaction.type == "expense":
            from app.services.budget_service import BudgetService
            budget_service = BudgetService(self.db)
            await budget_service.recalculate_budget_items(transaction.budget_id)

        transaction_dict["category"] = category_document["name"]
        return Transaction(**transaction_dict)
    
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID"""
        transaction = await self.collection.find_one({"_id": ObjectId(transaction_id)})
        if transaction:
            return await self._serialize_transaction_document(transaction)
        return None
    
    async def get_transactions(
        self,
        budget_id: Optional[str] = None,
        type_filter: Optional[str] = None,
        category: Optional[str] = None,
        category_id: Optional[str] = None,
        is_charged: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions with optional filters"""
        query = {}
        
        if budget_id:
            query["budget_id"] = budget_id
        if type_filter:
            query["type"] = type_filter
        category_query = await self._build_category_query(category=category, category_id=category_id)
        if category_query:
            query.update(category_query)
        if is_charged is not None:
            query["is_charged"] = is_charged
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("timestamp", -1)
        transactions = []
        
        async for transaction in cursor:
            transactions.append(transaction)

        return await self._serialize_transaction_documents(transactions)
    
    async def update_transaction(
        self, 
        transaction_id: str, 
        transaction_update: TransactionUpdate
    ) -> Optional[Transaction]:
        """Update a transaction"""
        # Get original transaction to know which budget to recalculate
        original = await self.get_transaction(transaction_id)
        if not original:
            return None
        
        update_data = {k: v for k, v in transaction_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_transaction(transaction_id)
        
        # Convert Decimal to float if amount is being updated
        if "amount" in update_data:
            update_data["amount"] = float(update_data["amount"])

        if "category_id" in update_data or "category" in update_data:
            category_document = await self._resolve_category_document(
                update_data.get("category_id"),
                update_data.get("category"),
                "Category not found for transaction",
            )
            update_data["category_id"] = category_document["_id"]
            update_data.pop("category", None)
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(transaction_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            updated_transaction = await self._serialize_transaction_document(result)
            
            # Recalculate budget items for affected budgets
            from app.services.budget_service import BudgetService
            budget_service = BudgetService(self.db)
            
            # Recalculate original budget if transaction was expense
            if original.type == "expense":
                await budget_service.recalculate_budget_items(original.budget_id)
            
            # If budget changed, recalculate new budget too
            if "budget_id" in update_data and update_data["budget_id"] != original.budget_id:
                if updated_transaction.type == "expense":
                    await budget_service.recalculate_budget_items(updated_transaction.budget_id)
            
            return updated_transaction
        return None
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction"""
        # Get transaction before deleting to recalculate budget
        transaction = await self.get_transaction(transaction_id)
        if not transaction:
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(transaction_id)})
        
        # Recalculate budget items if it was an expense
        if result.deleted_count > 0 and transaction.type == "expense":
            from app.services.budget_service import BudgetService
            budget_service = BudgetService(self.db)
            await budget_service.recalculate_budget_items(transaction.budget_id)
        
        return result.deleted_count > 0
    
    async def mark_as_charged(self, transaction_id: str, is_charged: bool = True) -> Optional[Transaction]:
        """Mark a transaction as charged or uncharged"""
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(transaction_id)},
            {"$set": {"is_charged": is_charged, "updated_at": datetime.utcnow()}},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return Transaction(**result)
        return None
    
    async def get_transactions_by_budget(self, budget_id: str) -> List[Transaction]:
        """Get all transactions for a specific budget"""
        return await self.get_transactions(budget_id=budget_id, limit=1000)
    
    async def bulk_create_transactions(self, transactions: List[TransactionCreate]) -> List[Transaction]:
        """Create multiple transactions at once"""
        transaction_dicts = []
        now = datetime.utcnow()
        category_maps = await load_category_reference_maps(self.db)
        
        for transaction in transactions:
            trans_dict = transaction.model_dump()
            category_document = require_category_document(
                category_maps,
                category_id=transaction.category_id,
                category_name=transaction.category,
                error_message="Category not found for transaction",
            )
            trans_dict["amount"] = float(trans_dict["amount"])
            trans_dict["category_id"] = category_document["_id"]
            trans_dict.pop("category", None)
            trans_dict["created_at"] = now
            trans_dict["updated_at"] = now
            transaction_dicts.append(trans_dict)
        
        result = await self.collection.insert_many(transaction_dicts)
        
        created_transactions = []
        for idx, inserted_id in enumerate(result.inserted_ids):
            transaction_dicts[idx]["_id"] = str(inserted_id)
            created_transactions.append(
                Transaction(**enrich_category_reference(transaction_dicts[idx], category_maps))
            )
        
        return created_transactions
