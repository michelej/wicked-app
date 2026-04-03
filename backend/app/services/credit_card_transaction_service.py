from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.credit_card_transaction import (
    CreditCardTransaction,
    CreditCardTransactionCreate,
    CreditCardTransactionUpdate,
)


class CreditCardTransactionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.credit_card_transactions

    async def create_transaction(
        self, transaction: CreditCardTransactionCreate
    ) -> CreditCardTransaction:
        transaction_dict = transaction.model_dump()
        transaction_dict["amount"] = float(transaction_dict["amount"])
        transaction_dict["payment_method"] = "credit"
        transaction_dict["created_at"] = datetime.utcnow()
        transaction_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(transaction_dict)
        transaction_dict["_id"] = str(result.inserted_id)

        return CreditCardTransaction(**transaction_dict)

    async def get_transaction(
        self, transaction_id: str
    ) -> Optional[CreditCardTransaction]:
        transaction = await self.collection.find_one({"_id": ObjectId(transaction_id)})
        if transaction:
            transaction["_id"] = str(transaction["_id"])
            return CreditCardTransaction(**transaction)
        return None

    async def get_transactions(
        self,
        budget_id: Optional[str] = None,
        credit_card: Optional[str] = None,
        type_filter: Optional[str] = None,
        category: Optional[str] = None,
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
        if category:
            query["category"] = category
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
            transaction["_id"] = str(transaction["_id"])
            transactions.append(CreditCardTransaction(**transaction))

        return transactions

    async def update_transaction(
        self, transaction_id: str, transaction_update: CreditCardTransactionUpdate
    ) -> Optional[CreditCardTransaction]:
        update_data = transaction_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_transaction(transaction_id)

        if "amount" in update_data:
            update_data["amount"] = float(update_data["amount"])

        update_data["payment_method"] = "credit"
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(transaction_id)},
            {"$set": update_data},
            return_document=True,
        )

        if result:
            result["_id"] = str(result["_id"])
            return CreditCardTransaction(**result)
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

        for transaction in transactions:
            transaction_dict = transaction.model_dump()
            transaction_dict["amount"] = float(transaction_dict["amount"])
            transaction_dict["payment_method"] = "credit"
            transaction_dict["created_at"] = now
            transaction_dict["updated_at"] = now
            transaction_dicts.append(transaction_dict)

        result = await self.collection.insert_many(transaction_dicts)

        created_transactions = []
        for idx, inserted_id in enumerate(result.inserted_ids):
            transaction_dicts[idx]["_id"] = str(inserted_id)
            created_transactions.append(CreditCardTransaction(**transaction_dicts[idx]))

        return created_transactions
