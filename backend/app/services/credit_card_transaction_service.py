from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.credit_card_transaction import (
    CreditCardTransaction,
    CreditCardTransactionCreate,
    CreditCardTransactionUpdate,
)
from app.utils.category_references import enrich_category_reference, load_category_reference_maps, require_category_document, resolve_category_document


class CreditCardTransactionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.credit_card_transactions

    async def _serialize_transaction_document(self, transaction: dict) -> CreditCardTransaction:
        category_maps = await load_category_reference_maps(self.db)
        enriched_transaction = enrich_category_reference({**transaction, "_id": str(transaction["_id"])}, category_maps)
        return CreditCardTransaction(**enriched_transaction)

    async def _serialize_transaction_documents(self, transactions: List[dict]) -> List[CreditCardTransaction]:
        category_maps = await load_category_reference_maps(self.db)
        return [
            CreditCardTransaction(**enrich_category_reference({**transaction, "_id": str(transaction["_id"])}, category_maps))
            for transaction in transactions
        ]

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

    async def create_transaction(
        self, transaction: CreditCardTransactionCreate
    ) -> CreditCardTransaction:
        transaction_dict = transaction.model_dump()
        category_document = require_category_document(
            await load_category_reference_maps(self.db),
            category_id=transaction.category_id,
            category_name=transaction.category,
            error_message="Category not found for credit card transaction",
        )
        transaction_dict["amount"] = float(transaction_dict["amount"])
        transaction_dict["category_id"] = category_document["_id"]
        transaction_dict.pop("category", None)
        transaction_dict["payment_method"] = "credit"
        transaction_dict["created_at"] = datetime.utcnow()
        transaction_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(transaction_dict)
        transaction_dict["_id"] = str(result.inserted_id)
        transaction_dict["category"] = category_document["name"]

        return CreditCardTransaction(**transaction_dict)

    async def get_transaction(
        self, transaction_id: str
    ) -> Optional[CreditCardTransaction]:
        transaction = await self.collection.find_one({"_id": ObjectId(transaction_id)})
        if transaction:
            return await self._serialize_transaction_document(transaction)
        return None

    async def get_transactions(
        self,
        budget_id: Optional[str] = None,
        credit_card: Optional[str] = None,
        type_filter: Optional[str] = None,
        category: Optional[str] = None,
        category_id: Optional[str] = None,
        is_charged: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CreditCardTransaction]:
        query = {}

        if budget_id:
            query["budget_id"] = budget_id
        if credit_card:
            query["credit_card"] = credit_card
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
        self, transaction_id: str, transaction_update: CreditCardTransactionUpdate
    ) -> Optional[CreditCardTransaction]:
        update_data = transaction_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_transaction(transaction_id)

        if "amount" in update_data:
            update_data["amount"] = float(update_data["amount"])

        if "category_id" in update_data or "category" in update_data:
            category_document = require_category_document(
                await load_category_reference_maps(self.db),
                category_id=update_data.get("category_id"),
                category_name=update_data.get("category"),
                error_message="Category not found for credit card transaction",
            )
            update_data["category_id"] = category_document["_id"]
            update_data.pop("category", None)

        update_data["payment_method"] = "credit"
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(transaction_id)},
            {"$set": update_data},
            return_document=True,
        )

        if result:
            return await self._serialize_transaction_document(result)
        return None

    async def delete_transaction(self, transaction_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(transaction_id)})
        return result.deleted_count > 0

    async def mark_as_charged(
        self, transaction_id: str, is_charged: bool = True
    ) -> Optional[CreditCardTransaction]:
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(transaction_id)},
            {"$set": {"is_charged": is_charged, "updated_at": datetime.utcnow()}},
            return_document=True,
        )

        if result:
            result["_id"] = str(result["_id"])
            return CreditCardTransaction(**result)
        return None

    async def bulk_create_transactions(
        self, transactions: List[CreditCardTransactionCreate]
    ) -> List[CreditCardTransaction]:
        transaction_dicts = []
        now = datetime.utcnow()
        category_maps = await load_category_reference_maps(self.db)

        for transaction in transactions:
            transaction_dict = transaction.model_dump()
            category_document = require_category_document(
                category_maps,
                category_id=transaction.category_id,
                category_name=transaction.category,
                error_message="Category not found for credit card transaction",
            )
            transaction_dict["amount"] = float(transaction_dict["amount"])
            transaction_dict["category_id"] = category_document["_id"]
            transaction_dict.pop("category", None)
            transaction_dict["payment_method"] = "credit"
            transaction_dict["created_at"] = now
            transaction_dict["updated_at"] = now
            transaction_dicts.append(transaction_dict)

        result = await self.collection.insert_many(transaction_dicts)

        created_transactions = []
        for idx, inserted_id in enumerate(result.inserted_ids):
            transaction_dicts[idx]["_id"] = str(inserted_id)
            created_transactions.append(
                CreditCardTransaction(**enrich_category_reference(transaction_dicts[idx], category_maps))
            )

        return created_transactions
