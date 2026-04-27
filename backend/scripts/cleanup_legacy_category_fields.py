import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env")

from app.core.config import settings


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("cleanup-legacy-category-fields")


FLAT_COLLECTIONS = (
    "transactions",
    "recurring_expenses",
    "credit_card_transactions",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove legacy category string fields after category_id migration.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without writing changes.")
    parser.add_argument(
        "--include-imported-transactions",
        action="store_true",
        help="Also remove processed_category from imported_transactions when processed_category_id exists.",
    )
    return parser.parse_args()


async def cleanup_flat_collection(
    db: AsyncIOMotorDatabase,
    collection_name: str,
    dry_run: bool,
) -> dict[str, int]:
    collection = db[collection_name]
    matched = 0
    updated = 0

    query = {
        "category_id": {"$exists": True, "$ne": None},
        "category": {"$exists": True},
    }

    async for document in collection.find(query):
        matched += 1

        if dry_run:
            logger.info(
                "[dry-run] %s %s -> remove category='%s' keep category_id='%s'",
                collection_name,
                str(document["_id"]),
                document.get("category"),
                document.get("category_id"),
            )
            updated += 1
            continue

        result = await collection.update_one(
            {"_id": document["_id"]},
            {
                "$unset": {"category": ""},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )
        updated += result.modified_count

    return {"matched": matched, "updated": updated}


async def cleanup_budget_items(
    db: AsyncIOMotorDatabase,
    dry_run: bool,
) -> dict[str, int]:
    matched = 0
    updated = 0

    async for budget in db.budgets.find({"budget_items.category": {"$exists": True}}):
        original_items = budget.get("budget_items", [])
        next_items = []
        changed = False

        for item in original_items:
            next_item = dict(item)
            has_category_id = next_item.get("category_id") is not None
            has_legacy_category = "category" in next_item

            if has_category_id and has_legacy_category:
                matched += 1
                changed = True
                legacy_category = next_item.pop("category", None)

                if dry_run:
                    logger.info(
                        "[dry-run] budgets %s -> remove item category='%s' keep category_id='%s'",
                        str(budget["_id"]),
                        legacy_category,
                        next_item.get("category_id"),
                    )

            next_items.append(next_item)

        if not changed:
            continue

        if dry_run:
            updated += 1
            continue

        result = await db.budgets.update_one(
            {"_id": budget["_id"]},
            {
                "$set": {
                    "budget_items": next_items,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        updated += result.modified_count

    return {"matched": matched, "updated": updated}


async def cleanup_imported_transactions(
    db: AsyncIOMotorDatabase,
    dry_run: bool,
) -> dict[str, int]:
    matched = 0
    updated = 0

    query = {
        "processed_category_id": {"$exists": True, "$ne": None},
        "processed_category": {"$exists": True},
    }

    async for document in db.imported_transactions.find(query):
        matched += 1

        if dry_run:
            logger.info(
                "[dry-run] imported_transactions %s -> remove processed_category='%s' keep processed_category_id='%s'",
                str(document["_id"]),
                document.get("processed_category"),
                document.get("processed_category_id"),
            )
            updated += 1
            continue

        result = await db.imported_transactions.update_one(
            {"_id": document["_id"]},
            {
                "$unset": {"processed_category": ""},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )
        updated += result.modified_count

    return {"matched": matched, "updated": updated}


async def main() -> None:
    args = parse_args()
    logger.info("Starting legacy category cleanup")
    logger.info("Backup recommendation: create a MongoDB backup before running without --dry-run")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    try:
        summaries = {}

        for collection_name in FLAT_COLLECTIONS:
            summaries[collection_name] = await cleanup_flat_collection(db, collection_name, args.dry_run)

        summaries["budgets"] = await cleanup_budget_items(db, args.dry_run)

        if args.include_imported_transactions:
            summaries["imported_transactions"] = await cleanup_imported_transactions(db, args.dry_run)

        logger.info("Cleanup completed")
        for collection_name, summary in summaries.items():
            logger.info("%s -> matched=%s updated=%s", collection_name, summary["matched"], summary["updated"])
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
