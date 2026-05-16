from datetime import datetime
from typing import Any, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.watch_item import WatchItem, WatchItemCreate, WatchItemUpdate


class WatchlistService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.watch_items

    async def get_items(
        self,
        status: Optional[str] = None,
        media_type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[WatchItem]:
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if media_type:
            query["media_type"] = media_type
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"original_title": {"$regex": search, "$options": "i"}},
                {"overview": {"$regex": search, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": search, "$options": "i"}}},
            ]

        cursor = self.collection.find(query).skip(skip).limit(limit).sort([
            ("status", 1),
            ("updated_at", -1),
            ("created_at", -1),
        ])
        items = []
        async for document in cursor:
            items.append(self._serialize_item(document))
        return items

    async def get_item(self, item_id: str) -> Optional[WatchItem]:
        document = await self.collection.find_one({"_id": ObjectId(item_id)})
        if not document:
            return None
        return self._serialize_item(document)

    async def create_item(self, payload: WatchItemCreate) -> WatchItem:
        document = payload.model_dump()
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()

        existing = await self.collection.find_one({
            "tmdb_id": payload.tmdb_id,
            "media_type": payload.media_type,
        })
        if existing:
            raise ValueError("Ese título ya está en tu lista")

        result = await self.collection.insert_one(document)
        return await self.get_item(str(result.inserted_id))

    async def update_item(self, item_id: str, payload: WatchItemUpdate) -> Optional[WatchItem]:
        update_data = {key: value for key, value in payload.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_item(item_id)

        update_data["updated_at"] = datetime.utcnow()
        document = await self.collection.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": update_data},
            return_document=True,
        )
        if not document:
            return None
        return self._serialize_item(document)

    async def delete_item(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0

    def _serialize_item(self, document: dict[str, Any]) -> WatchItem:
        document["_id"] = str(document["_id"])
        return WatchItem(**document)
