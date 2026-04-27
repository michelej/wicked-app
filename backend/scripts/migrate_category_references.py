import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env")

from app.core.config import settings


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("migrate-category-references")


CATEGORIZED_COLLECTIONS = (
    "transactions",
    "recurring_expenses",
    "credit_card_transactions",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill category_id references across MongoDB collections.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned updates without writing to MongoDB.")
    parser.add_argument(
        "--create-missing",
        action="store_true",
        help="Create missing categories from legacy names instead of assigning Uncategorized.",
    )
    parser.add_argument(
        "--drop-legacy-category",
        action="store_true",
        help="Remove the legacy category string field after assigning category_id.",
    )
    parser.add_argument(
        "--uncategorized-name",
        default="Uncategorized",
        help="Fallback category name when legacy values cannot be matched.",
    )
    return parser.parse_args()


async def load_category_maps(db: AsyncIOMotorDatabase) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}

    async for category in db.categories.find({}):
        serialized_category = {**category, "_id": str(category["_id"])}
        by_id[serialized_category["_id"]] = serialized_category
        by_name[serialized_category["name"]] = serialized_category

    return by_id, by_name


async def ensure_category(
    db: AsyncIOMotorDatabase,
    by_name: dict[str, dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
    category_name: str,
    category_type: str,
) -> dict[str, Any]:
    if category_name in by_name:
        return by_name[category_name]

    category_document = {
        "name": category_name,
        "type": category_type,
        "icon": "pi pi-tag",
        "color": "#64748B",
        "parent_id": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.categories.insert_one(category_document)
    serialized_category = {**category_document, "_id": str(result.inserted_id)}
    by_name[category_name] = serialized_category
    by_id[serialized_category["_id"]] = serialized_category
    logger.info("Created missing category '%s' (%s)", category_name, category_type)
    return serialized_category


async def resolve_category_id(
    db: AsyncIOMotorDatabase,
    by_name: dict[str, dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
    legacy_category_name: Optional[str],
    category_type_hint: str,
    create_missing: bool,
    uncategorized_name: str,
) -> Optional[str]:
    normalized_name = str(legacy_category_name).strip() if legacy_category_name else None
    if normalized_name and normalized_name in by_name:
        return by_name[normalized_name]["_id"]

    if normalized_name and create_missing:
        created_category = await ensure_category(db, by_name, by_id, normalized_name, category_type_hint)
        return created_category["_id"]

    fallback_category = await ensure_category(db, by_name, by_id, uncategorized_name, "both")
    return fallback_category["_id"]


async def migrate_flat_collection(
    db: AsyncIOMotorDatabase,
    collection_name: str,
    by_name: dict[str, dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
    dry_run: bool,
    create_missing: bool,
    drop_legacy_category: bool,
    uncategorized_name: str,
) -> dict[str, int]:
    collection = db[collection_name]
    matched = 0
    updated = 0

    async for document in collection.find({}):
        matched += 1
        legacy_category_name = document.get("category")
        category_type_hint = document.get("type", "both")
        resolved_category_id = await resolve_category_id(
            db,
            by_name,
            by_id,
            legacy_category_name,
            category_type_hint,
            create_missing,
            uncategorized_name,
        )

        update_payload: dict[str, Any] = {"category_id": resolved_category_id, "updated_at": datetime.utcnow()}
        update_operation: dict[str, Any] = {"$set": update_payload}

        if drop_legacy_category and "category" in document:
            update_operation["$unset"] = {"category": ""}

        if dry_run:
            logger.info(
                "[dry-run] %s %s -> category='%s' category_id='%s'",
                collection_name,
                str(document["_id"]),
                legacy_category_name,
                resolved_category_id,
            )
            updated += 1
            continue

        result = await collection.update_one({"_id": document["_id"]}, update_operation)
        updated += result.modified_count

    return {"matched": matched, "updated": updated}


async def migrate_budgets(
    db: AsyncIOMotorDatabase,
    by_name: dict[str, dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
    dry_run: bool,
    create_missing: bool,
    drop_legacy_category: bool,
    uncategorized_name: str,
) -> dict[str, int]:
    matched = 0
    updated = 0

    async for budget in db.budgets.find({}):
        matched += 1
        original_items = budget.get("budget_items", [])
        migrated_items = []

        for item in original_items:
            legacy_category_name = item.get("category")
            resolved_category_id = await resolve_category_id(
                db,
                by_name,
                by_id,
                legacy_category_name,
                "both",
                create_missing,
                uncategorized_name,
            )

            migrated_item = {
                "category_id": resolved_category_id,
                "planned_amount": item.get("planned_amount", 0),
                "spent_amount": item.get("spent_amount", 0),
            }

            if not drop_legacy_category and legacy_category_name:
                migrated_item["category"] = legacy_category_name

            migrated_items.append(migrated_item)

        if dry_run:
            logger.info("[dry-run] budgets %s -> %s items migrated", str(budget["_id"]), len(migrated_items))
            updated += 1
            continue

        result = await db.budgets.update_one(
            {"_id": budget["_id"]},
            {"$set": {"budget_items": migrated_items, "updated_at": datetime.utcnow()}},
        )
        updated += result.modified_count

    return {"matched": matched, "updated": updated}


async def main() -> None:
    args = parse_args()
    logger.info("Starting category reference migration")
    logger.info("Backup recommendation: create a MongoDB backup before running without --dry-run")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    try:
        by_id, by_name = await load_category_maps(db)

        summaries = {}
        for collection_name in CATEGORIZED_COLLECTIONS:
            summaries[collection_name] = await migrate_flat_collection(
                db,
                collection_name,
                by_name,
                by_id,
                args.dry_run,
                args.create_missing,
                args.drop_legacy_category,
                args.uncategorized_name,
            )

        summaries["budgets"] = await migrate_budgets(
            db,
            by_name,
            by_id,
            args.dry_run,
            args.create_missing,
            args.drop_legacy_category,
            args.uncategorized_name,
        )

        logger.info("Migration completed")
        for collection_name, summary in summaries.items():
            logger.info("%s -> matched=%s updated=%s", collection_name, summary["matched"], summary["updated"])
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
