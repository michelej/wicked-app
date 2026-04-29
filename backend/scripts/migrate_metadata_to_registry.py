import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env")

from app.core.config import settings


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("migrate-metadata-to-registry")


TYPE_ALIASES = {
    "fecha": "date",
    "date": "date",
    "trip": "trip",
    "travel": "trip",
    "viaje": "trip",
    "purchase": "purchase",
    "compra": "purchase",
    "warranty": "warranty",
    "garantia": "warranty",
    "document": "document",
    "documento": "document",
    "event": "event",
    "evento": "event",
    "note": "note",
    "nota": "note",
    "subscription": "subscription",
    "suscripcion": "subscription",
    "task": "task",
    "tarea": "task",
    "procedure": "procedure",
    "tramite": "procedure",
    "other": "other",
    "otro": "other",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate legacy metadata collection into registry_items.")
    parser.add_argument("--dry-run", action="store_true", help="Inspect the migration without writing to MongoDB.")
    parser.add_argument("--source-collection", default="metadata", help="Legacy source collection name.")
    parser.add_argument("--target-collection", default="registry_items", help="Target collection name.")
    parser.add_argument("--replace", action="store_true", help="Replace already migrated items with the same legacy reference.")
    return parser.parse_args()


def normalize_type(value: Any) -> str:
    normalized_value = str(value or "other").strip().lower()
    return TYPE_ALIASES.get(normalized_value, "other")


def normalize_status(value: Any) -> str:
    normalized_value = str(value or "active").strip().lower()
    allowed_statuses = {"active", "planned", "completed", "cancelled", "archived"}
    return normalized_value if normalized_value in allowed_statuses else "active"


def as_datetime(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    return None


def parse_tags(document: dict[str, Any]) -> list[str]:
    tags = document.get("tags") or document.get("labels") or []
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not isinstance(tags, list):
        return []
    return [str(tag).strip() for tag in tags if str(tag).strip()]


def parse_custom_fields(document: dict[str, Any]) -> list[dict[str, Any]]:
    explicit_fields = document.get("customFields") or document.get("custom_fields") or []
    if isinstance(explicit_fields, list):
        return explicit_fields

    if isinstance(explicit_fields, dict):
        return [
            {
                "key": key,
                "label": str(key).replace("_", " ").title(),
                "type": "text",
                "value": value,
            }
            for key, value in explicit_fields.items()
        ]

    legacy_payload = document.get("data") or document.get("details") or {}
    if isinstance(legacy_payload, dict):
        return [
            {
                "key": key,
                "label": str(key).replace("_", " ").title(),
                "type": "text",
                "value": value,
            }
            for key, value in legacy_payload.items()
        ]

    return []


def migrate_document(document: dict[str, Any], source_collection: str) -> dict[str, Any]:
    title = document.get("title") or document.get("name") or document.get("text") or f"Registro {document['_id']}"
    legacy_type = document.get("type") or document.get("category") or document.get("kind")

    payload = {
        "title": str(title).strip(),
        "description": document.get("description") or document.get("content") or document.get("notes"),
        "type": normalize_type(legacy_type),
        "status": normalize_status(document.get("status")),
        "date": as_datetime(document.get("date")),
        "startDate": as_datetime(document.get("startDate") or document.get("start_date")),
        "endDate": as_datetime(document.get("endDate") or document.get("end_date")),
        "amount": document.get("amount"),
        "currency": document.get("currency"),
        "location": document.get("location") or document.get("place"),
        "tags": parse_tags(document),
        "relatedEntities": document.get("relatedEntities") or document.get("related_entities") or [],
        "customFields": parse_custom_fields(document),
        "attachments": document.get("attachments") or [],
        "createdAt": as_datetime(document.get("createdAt") or document.get("created_at")) or datetime.utcnow(),
        "updatedAt": as_datetime(document.get("updatedAt") or document.get("updated_at")) or datetime.utcnow(),
        "legacySource": {
            "collection": source_collection,
            "legacyId": str(document["_id"]),
        },
    }

    return payload


async def migrate_metadata_collection(
    db: AsyncIOMotorDatabase,
    source_collection: str,
    target_collection: str,
    dry_run: bool,
    replace: bool,
) -> tuple[int, int]:
    matched = 0
    migrated = 0

    async for document in db[source_collection].find({}):
        matched += 1
        payload = migrate_document(document, source_collection)
        legacy_reference = payload["legacySource"]

        if dry_run:
            logger.info("[dry-run] %s -> %s (%s)", str(document["_id"]), payload["title"], payload["type"])
            migrated += 1
            continue

        query = {"legacySource.collection": legacy_reference["collection"], "legacySource.legacyId": legacy_reference["legacyId"]}
        if replace:
            result = await db[target_collection].update_one(query, {"$set": payload}, upsert=True)
            migrated += 1 if result.upserted_id or result.modified_count >= 0 else 0
            continue

        existing = await db[target_collection].find_one(query)
        if existing:
            logger.info("Skipping %s because it was already migrated", str(document["_id"]))
            continue

        await db[target_collection].insert_one(payload)
        migrated += 1

    return matched, migrated


async def main() -> None:
    args = parse_args()
    logger.info("Starting metadata -> registry migration")
    logger.info("Backup recommendation: create a MongoDB backup before running without --dry-run")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    try:
        collection_names = await db.list_collection_names()
        if args.source_collection not in collection_names:
            logger.warning("Source collection '%s' was not found. Nothing to migrate.", args.source_collection)
            return

        matched, migrated = await migrate_metadata_collection(
            db,
            args.source_collection,
            args.target_collection,
            args.dry_run,
            args.replace,
        )
        logger.info("Migration completed: matched=%s migrated=%s", matched, migrated)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
