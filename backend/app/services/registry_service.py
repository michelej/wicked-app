from datetime import datetime
from typing import Any, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.registry_item import RegistryItem, RegistryItemCreate, RegistryItemUpdate


class RegistryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.registry_items

    async def create_item(self, item: RegistryItemCreate) -> RegistryItem:
        payload = item.model_dump()
        payload["createdAt"] = datetime.utcnow()
        payload["updatedAt"] = datetime.utcnow()

        result = await self.collection.insert_one(payload)
        return await self.get_item(str(result.inserted_id))

    async def get_item(self, item_id: str) -> Optional[RegistryItem]:
        document = await self.collection.find_one({"_id": ObjectId(item_id)})
        if not document:
            return None

        return self._serialize_item(document)

    async def get_items(
        self,
        type_filter: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        location: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[RegistryItem]:
        query = self._build_query(
            type_filter=type_filter,
            status=status,
            tags=tags,
            search=search,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            location=location,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

        cursor = self.collection.find(query).skip(skip).limit(limit).sort([
            ("date", -1),
            ("startDate", -1),
            ("createdAt", -1),
        ])
        items = []
        async for document in cursor:
            items.append(self._serialize_item(document))
        return items

    async def update_item(self, item_id: str, item_update: RegistryItemUpdate) -> Optional[RegistryItem]:
        update_data = {key: value for key, value in item_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_item(item_id)

        update_data["updatedAt"] = datetime.utcnow()
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

    async def archive_item(self, item_id: str) -> Optional[RegistryItem]:
        return await self.update_item(item_id, RegistryItemUpdate(status="archived"))

    async def duplicate_item(self, item_id: str) -> Optional[RegistryItem]:
        source_item = await self.get_item(item_id)
        if not source_item:
            return None

        source_payload = source_item.model_dump(by_alias=False)
        source_payload.pop("id", None)
        source_payload.pop("createdAt", None)
        source_payload.pop("updatedAt", None)
        source_payload["title"] = f"{source_item.title} (copia)"
        source_payload["status"] = "planned" if source_item.status != "archived" else "active"

        return await self.create_item(RegistryItemCreate(**source_payload))

    def _serialize_item(self, document: dict[str, Any]) -> RegistryItem:
        document["_id"] = str(document["_id"])
        return RegistryItem(**document)

    def _build_query(
        self,
        type_filter: Optional[str],
        status: Optional[str],
        tags: Optional[List[str]],
        search: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        min_amount: Optional[float],
        max_amount: Optional[float],
        location: Optional[str],
        related_entity_type: Optional[str],
        related_entity_id: Optional[str],
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}

        if type_filter:
            query["type"] = type_filter

        if status:
            query["status"] = status

        if tags:
            query["tags"] = {"$in": tags}

        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": search, "$options": "i"}}},
                {"customFields.label": {"$regex": search, "$options": "i"}},
                {"customFields.value": {"$regex": search, "$options": "i"}},
            ]

        if start_date or end_date:
            date_clauses = []
            if start_date:
                date_clauses.extend([
                    {"date": {"$gte": start_date}},
                    {"startDate": {"$gte": start_date}},
                    {"endDate": {"$gte": start_date}},
                ])
            if end_date:
                date_clauses.extend([
                    {"date": {"$lte": end_date}},
                    {"startDate": {"$lte": end_date}},
                    {"endDate": {"$lte": end_date}},
                ])
            query.setdefault("$and", []).append({"$or": date_clauses})

        if min_amount is not None or max_amount is not None:
            amount_query: dict[str, Any] = {}
            if min_amount is not None:
                amount_query["$gte"] = min_amount
            if max_amount is not None:
                amount_query["$lte"] = max_amount
            query["amount"] = amount_query

        if location:
            query["location"] = {"$regex": location, "$options": "i"}

        if related_entity_type:
            query["relatedEntities.entityType"] = related_entity_type

        if related_entity_id:
            query["relatedEntities.entityId"] = related_entity_id

        return query
