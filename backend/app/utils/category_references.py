from dataclasses import dataclass
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


@dataclass
class CategoryReferenceMaps:
    by_id: dict[str, dict[str, Any]]
    by_name: dict[str, dict[str, Any]]


async def load_category_reference_maps(db: AsyncIOMotorDatabase) -> CategoryReferenceMaps:
    by_id: dict[str, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}

    async for category in db.categories.find({}):
        serialized_category = {
            **category,
            "_id": str(category["_id"]),
        }
        by_id[serialized_category["_id"]] = serialized_category
        by_name[serialized_category["name"]] = serialized_category

    return CategoryReferenceMaps(by_id=by_id, by_name=by_name)


def resolve_category_document(
    category_maps: CategoryReferenceMaps,
    category_id: Optional[str] = None,
    category_name: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    normalized_category_id = str(category_id).strip() if category_id else None
    normalized_category_name = str(category_name).strip() if category_name else None

    if normalized_category_id and normalized_category_id in category_maps.by_id:
        return category_maps.by_id[normalized_category_id]

    if normalized_category_name and normalized_category_name in category_maps.by_name:
        return category_maps.by_name[normalized_category_name]

    return None


def require_category_document(
    category_maps: CategoryReferenceMaps,
    category_id: Optional[str] = None,
    category_name: Optional[str] = None,
    error_message: str = "Category not found",
) -> dict[str, Any]:
    category_document = resolve_category_document(category_maps, category_id=category_id, category_name=category_name)
    if category_document:
        return category_document

    raise ValueError(error_message)


def enrich_category_reference(
    document: dict[str, Any],
    category_maps: CategoryReferenceMaps,
    category_field: str = "category",
    category_id_field: str = "category_id",
) -> dict[str, Any]:
    category_document = resolve_category_document(
        category_maps,
        category_id=document.get(category_id_field),
        category_name=document.get(category_field),
    )

    if category_document:
        document[category_id_field] = category_document["_id"]
        document[category_field] = category_document["name"]
        return document

    legacy_category_name = document.get(category_field)
    if legacy_category_name:
        document[category_field] = legacy_category_name

    if document.get(category_id_field) is not None:
        document[category_id_field] = str(document[category_id_field])

    return document


def get_parent_category_name(
    category_maps: CategoryReferenceMaps,
    category_id: Optional[str] = None,
    category_name: Optional[str] = None,
) -> Optional[str]:
    category_document = resolve_category_document(category_maps, category_id=category_id, category_name=category_name)
    if not category_document:
        return None

    parent_id = category_document.get("parent_id")
    if not parent_id:
        return None

    parent_category = category_maps.by_id.get(str(parent_id))
    return parent_category["name"] if parent_category else None
