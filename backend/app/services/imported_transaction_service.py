from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO
from typing import Any, Dict, List, Optional
from zipfile import ZipFile
import xml.etree.ElementTree as element_tree

import xlrd
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.imported_transaction import (
    ImportedTransaction,
    ImportedTransactionProcess,
    ImportedTransactionsUploadResponse,
)
from app.models.transaction import TransactionCreate
from app.services.transaction_service import TransactionService


SPREADSHEET_NS = {"sheet": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BBVA_REQUIRED_HEADERS = [
    "F.Valor",
    "Fecha",
    "Concepto",
    "Movimiento",
    "Importe",
    "Divisa",
    "Disponible",
    "Observaciones",
]
ING_REQUIRED_HEADERS = [
    "F. VALOR",
    "CATEGORÍA",
    "SUBCATEGORÍA",
    "DESCRIPCIÓN",
    "COMENTARIO",
    "IMPORTE (€)",
    "SALDO (€)",
]


class ImportedTransactionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.imported_transactions

    async def get_imported_transactions(
        self,
        status: Optional[str] = None,
        source_bank: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[ImportedTransaction]:
        query: Dict[str, Any] = {}

        if status:
            query["status"] = status
        if source_bank:
            query["source_bank"] = source_bank

        cursor = self.collection.find(query).skip(skip).limit(limit).sort("suggested_timestamp", -1)
        transactions: List[ImportedTransaction] = []

        async for item in cursor:
            item["_id"] = str(item["_id"])
            transactions.append(ImportedTransaction(**item))

        return transactions

    async def get_imported_transaction(self, imported_transaction_id: str) -> Optional[ImportedTransaction]:
        item = await self.collection.find_one({"_id": ObjectId(imported_transaction_id)})
        if not item:
            return None

        item["_id"] = str(item["_id"])
        return ImportedTransaction(**item)

    async def upload_transactions(self, source_bank: str, file_name: str, content: bytes) -> ImportedTransactionsUploadResponse:
        if source_bank == "bbva":
            parsed_rows = parse_bbva_workbook(content, file_name)
        elif source_bank == "ing_direct":
            parsed_rows = parse_ing_workbook(content, file_name)
        else:
            raise ValueError("Banco no soportado.")

        if not parsed_rows:
            return ImportedTransactionsUploadResponse(
                source_bank=source_bank,
                file_name=file_name,
                total_rows=0,
                imported_count=0,
                duplicate_count=0,
                pending_count=0,
                preview=[],
            )

        fingerprints = [row["fingerprint"] for row in parsed_rows]
        existing_fingerprints = await self.collection.distinct("fingerprint", {"fingerprint": {"$in": fingerprints}})
        now = datetime.utcnow()

        rows_to_insert = []
        for row in parsed_rows:
            if row["fingerprint"] in existing_fingerprints:
                continue

            row["created_at"] = now
            row["updated_at"] = now
            rows_to_insert.append(row)

        created_items: List[ImportedTransaction] = []
        if rows_to_insert:
            result = await self.collection.insert_many(rows_to_insert)
            for index, inserted_id in enumerate(result.inserted_ids):
                rows_to_insert[index]["_id"] = str(inserted_id)
                created_items.append(ImportedTransaction(**rows_to_insert[index]))

        pending_count = await self.collection.count_documents({"status": "pending", "source_bank": source_bank})
        duplicate_count = len(parsed_rows) - len(rows_to_insert)

        return ImportedTransactionsUploadResponse(
            source_bank=source_bank,
            file_name=file_name,
            total_rows=len(parsed_rows),
            imported_count=len(rows_to_insert),
            duplicate_count=duplicate_count,
            pending_count=pending_count,
            preview=created_items[:5],
        )

    async def process_imported_transaction(
        self,
        imported_transaction_id: str,
        payload: ImportedTransactionProcess,
    ) -> Optional[ImportedTransaction]:
        imported_transaction = await self.get_imported_transaction(imported_transaction_id)
        if not imported_transaction:
            return None

        if imported_transaction.status != "pending":
            raise ValueError("La transacción importada ya fue procesada.")

        resolved_type = payload.type or imported_transaction.type
        resolved_comment = payload.comment or imported_transaction.comment_suggestion
        resolved_timestamp = payload.timestamp or imported_transaction.suggested_timestamp or imported_transaction.value_date or imported_transaction.booking_date or datetime.utcnow()
        resolved_bank = payload.bank or normalize_bank_label(imported_transaction.source_bank)

        update_data: Dict[str, Any] = {
            "processed_budget_id": payload.budget_id,
            "processed_category": payload.category,
            "processed_bank": resolved_bank,
            "processed_payment_method": payload.payment_method,
            "processed_comment": resolved_comment,
            "processed_timestamp": resolved_timestamp,
            "processed_is_charged": payload.is_charged,
            "processed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        if payload.import_to_system:
            if not payload.budget_id or not payload.category or not payload.payment_method:
                raise ValueError("Para incorporar la transacción al sistema debes seleccionar presupuesto, categoría y método de pago.")

            transaction_service = TransactionService(self.db)
            created_transaction = await transaction_service.create_transaction(
                TransactionCreate(
                    budget_id=payload.budget_id,
                    type=resolved_type,
                    amount=imported_transaction.amount,
                    category=payload.category,
                    bank=resolved_bank,
                    payment_method=payload.payment_method,
                    comment=resolved_comment,
                    timestamp=resolved_timestamp,
                    is_charged=payload.is_charged,
                )
            )
            update_data["status"] = "processed_imported"
            update_data["processed_transaction_id"] = created_transaction.id
        else:
            update_data["status"] = "processed_skipped"
            update_data["processed_transaction_id"] = None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(imported_transaction_id)},
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            return None

        result["_id"] = str(result["_id"])
        return ImportedTransaction(**result)


def parse_bbva_workbook(content: bytes, file_name: str) -> List[Dict[str, Any]]:
    rows = read_xlsx_rows(content)
    header_index = find_header_row_index(rows, BBVA_REQUIRED_HEADERS)
    if header_index is None:
        raise ValueError("No se encontraron las columnas esperadas en el Excel de BBVA.")

    header_row = rows[header_index]
    headers = [normalize_header(value) for value in header_row]
    header_map = {header: index for index, header in enumerate(headers) if header}

    parsed_rows: List[Dict[str, Any]] = []
    for row_offset, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
        if not any(str(cell).strip() for cell in row):
            continue

        mapped_row = get_row_values(row, header_map)
        if not mapped_row.get("Importe"):
            continue

        amount_value = parse_decimal(mapped_row.get("Importe"))
        if amount_value is None or amount_value == Decimal("0"):
            continue

        comment_suggestion = build_comment_suggestion(mapped_row.get("Concepto"), mapped_row.get("Observaciones"))
        parsed_rows.append(
            {
                "source_bank": "bbva",
                "source_file_name": file_name,
                "source_row_number": row_offset,
                "fingerprint": build_fingerprint("bbva", mapped_row, amount_value),
                "type": "expense" if amount_value < 0 else "income",
                "amount": float(abs(amount_value)),
                "currency": sanitize_text(mapped_row.get("Divisa")) or "EUR",
                "value_date": parse_excel_date(mapped_row.get("F.Valor")),
                "booking_date": parse_excel_date(mapped_row.get("Fecha")),
                "suggested_timestamp": build_suggested_timestamp(mapped_row.get("F.Valor"), mapped_row.get("Fecha")),
                "raw_concept": sanitize_text(mapped_row.get("Concepto")),
                "raw_movement": sanitize_text(mapped_row.get("Movimiento")),
                "raw_observations": sanitize_text(mapped_row.get("Observaciones")),
                "comment_suggestion": comment_suggestion,
                "payment_method_suggestion": suggest_payment_method(mapped_row.get("Movimiento")),
                "available_balance": to_float_or_none(parse_decimal(mapped_row.get("Disponible"))),
                "raw_payload": {
                    "value_date": sanitize_text(mapped_row.get("F.Valor")),
                    "booking_date": sanitize_text(mapped_row.get("Fecha")),
                    "concept": sanitize_text(mapped_row.get("Concepto")),
                    "movement": sanitize_text(mapped_row.get("Movimiento")),
                    "amount": sanitize_text(mapped_row.get("Importe")),
                    "currency": sanitize_text(mapped_row.get("Divisa")),
                    "available_balance": sanitize_text(mapped_row.get("Disponible")),
                    "observations": sanitize_text(mapped_row.get("Observaciones")),
                },
                "status": "pending",
                "processed_transaction_id": None,
                "processed_budget_id": None,
                "processed_category": None,
                "processed_bank": None,
                "processed_payment_method": None,
                "processed_comment": None,
                "processed_timestamp": None,
                "processed_is_charged": None,
                "processed_at": None,
            }
        )

    return parsed_rows


def parse_ing_workbook(content: bytes, file_name: str) -> List[Dict[str, Any]]:
    workbook = xlrd.open_workbook(file_contents=content)
    sheet = workbook.sheet_by_index(0)

    rows: List[List[Any]] = []
    for row_index in range(sheet.nrows):
        rows.append([sheet.cell_value(row_index, column_index) for column_index in range(sheet.ncols)])

    header_index = find_header_row_index(rows, ING_REQUIRED_HEADERS)
    if header_index is None:
        raise ValueError("No se encontraron las columnas esperadas en el Excel de ING Direct.")

    header_row = rows[header_index]
    headers = [normalize_header(value) for value in header_row]
    header_map = {header: index for index, header in enumerate(headers) if header}

    parsed_rows: List[Dict[str, Any]] = []
    for row_offset, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
        if not any(str(cell).strip() for cell in row):
            continue

        category = get_cell(row, header_map.get("CATEGORÍA"))
        subcategory = get_cell(row, header_map.get("SUBCATEGORÍA"))
        description = get_cell(row, header_map.get("DESCRIPCIÓN"))
        comment = get_cell(row, header_map.get("COMENTARIO"))
        amount_raw = get_cell(row, header_map.get("IMPORTE (€)"))
        balance_raw = get_cell(row, header_map.get("SALDO (€)"))
        date_raw = get_cell(row, header_map.get("F. VALOR"))

        amount_value = parse_decimal(amount_raw)
        if amount_value is None or amount_value == Decimal("0"):
            continue

        movement_label = " / ".join(part for part in [sanitize_text(category), sanitize_text(subcategory)] if part)
        booking_date = parse_ing_excel_date(date_raw, workbook.datemode)
        comment_suggestion = build_comment_suggestion(description, comment)

        parsed_rows.append(
            {
                "source_bank": "ing_direct",
                "source_file_name": file_name,
                "source_row_number": row_offset,
                "fingerprint": build_fingerprint(
                    "ing_direct",
                    {
                        "F.Valor": date_raw,
                        "Fecha": date_raw,
                        "Concepto": description,
                        "Movimiento": movement_label,
                        "Observaciones": comment,
                    },
                    amount_value,
                ),
                "type": "expense" if amount_value < 0 else "income",
                "amount": float(abs(amount_value)),
                "currency": "EUR",
                "value_date": booking_date,
                "booking_date": booking_date,
                "suggested_timestamp": datetime.combine(booking_date.date(), time(hour=12, minute=0)) if booking_date else None,
                "raw_concept": sanitize_text(description),
                "raw_movement": movement_label or None,
                "raw_observations": sanitize_text(comment),
                "comment_suggestion": comment_suggestion,
                "payment_method_suggestion": suggest_payment_method(description),
                "available_balance": to_float_or_none(parse_decimal(balance_raw)),
                "raw_payload": {
                    "value_date": sanitize_text(date_raw),
                    "category": sanitize_text(category),
                    "subcategory": sanitize_text(subcategory),
                    "description": sanitize_text(description),
                    "comment": sanitize_text(comment),
                    "amount": sanitize_text(amount_raw),
                    "balance": sanitize_text(balance_raw),
                },
                "status": "pending",
                "processed_transaction_id": None,
                "processed_budget_id": None,
                "processed_category": None,
                "processed_bank": None,
                "processed_payment_method": None,
                "processed_comment": None,
                "processed_timestamp": None,
                "processed_is_charged": None,
                "processed_at": None,
            }
        )

    return parsed_rows


def read_xlsx_rows(content: bytes) -> List[List[str]]:
    with ZipFile(BytesIO(content)) as workbook:
        shared_strings = read_shared_strings(workbook)
        sheet_name = first_sheet_name(workbook)
        sheet_xml = workbook.read(sheet_name)

    root = element_tree.fromstring(sheet_xml)
    rows: List[List[str]] = []

    for row in root.findall(".//sheet:sheetData/sheet:row", SPREADSHEET_NS):
        cell_map: Dict[int, str] = {}
        max_column = -1

        for cell in row.findall("sheet:c", SPREADSHEET_NS):
            ref = cell.get("r", "A1")
            column_index = excel_column_to_index(ref)
            max_column = max(max_column, column_index)
            cell_map[column_index] = parse_cell_value(cell, shared_strings)

        if max_column < 0:
            rows.append([])
            continue

        rows.append([cell_map.get(index, "") for index in range(max_column + 1)])

    return rows


def read_shared_strings(workbook: ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in workbook.namelist():
        return []

    root = element_tree.fromstring(workbook.read("xl/sharedStrings.xml"))
    strings: List[str] = []
    for item in root.findall("sheet:si", SPREADSHEET_NS):
        strings.append("".join(node.text or "" for node in item.findall(".//sheet:t", SPREADSHEET_NS)))
    return strings


def first_sheet_name(workbook: ZipFile) -> str:
    workbook_xml = element_tree.fromstring(workbook.read("xl/workbook.xml"))
    sheets = workbook_xml.findall(".//sheet:sheets/sheet:sheet", SPREADSHEET_NS)
    if not sheets:
        return "xl/worksheets/sheet1.xml"

    first_sheet = sheets[0]
    relationship_id = first_sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    relationships_xml = element_tree.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
    for relationship in relationships_xml.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
        if relationship.get("Id") == relationship_id:
            target = relationship.get("Target", "worksheets/sheet1.xml").lstrip("/")
            return target if target.startswith("xl/") else f"xl/{target}"
    return "xl/worksheets/sheet1.xml"


def parse_cell_value(cell: element_tree.Element, shared_strings: List[str]) -> str:
    value = cell.find("sheet:v", SPREADSHEET_NS)
    inline_value = cell.find("sheet:is", SPREADSHEET_NS)
    cell_type = cell.get("t")

    if cell_type == "s" and value is not None and value.text is not None:
        return shared_strings[int(value.text)]
    if inline_value is not None:
        return "".join(node.text or "" for node in inline_value.findall(".//sheet:t", SPREADSHEET_NS))
    return value.text if value is not None and value.text is not None else ""


def excel_column_to_index(reference: str) -> int:
    letters = ""
    for char in reference:
        if char.isalpha():
            letters += char.upper()
        else:
            break

    column_index = 0
    for char in letters:
        column_index = column_index * 26 + (ord(char) - 64)
    return max(column_index - 1, 0)


def normalize_header(value: Any) -> str:
    return str(value or "").strip()


def find_header_row_index(rows: List[List[str]], required_headers: List[str]) -> Optional[int]:
    required = {normalize_header(header) for header in required_headers}
    for index, row in enumerate(rows):
        normalized_row = {normalize_header(value) for value in row if normalize_header(value)}
        if required.issubset(normalized_row):
            return index
    return None


def get_row_values(row: List[str], header_map: Dict[str, int]) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for header, index in header_map.items():
        values[header] = row[index] if index < len(row) else ""
    return values


def get_cell(row: List[Any], index: Optional[int]) -> Any:
    if index is None or index >= len(row):
        return None
    return row[index]


def parse_excel_date(raw_value: Any) -> Optional[datetime]:
    text = sanitize_text(raw_value)
    if not text:
        return None

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_ing_excel_date(raw_value: Any, datemode: int) -> Optional[datetime]:
    if raw_value in (None, ""):
        return None

    if isinstance(raw_value, (int, float)):
        try:
            normalized_datemode = 1 if datemode == 1 else 0
            return xlrd.xldate.xldate_as_datetime(raw_value, normalized_datemode)
        except (ValueError, xlrd.xldate.XLDateError):
            return None

    return parse_excel_date(raw_value)


def build_suggested_timestamp(value_date: Any, booking_date: Any) -> Optional[datetime]:
    date_value = parse_excel_date(value_date) or parse_excel_date(booking_date)
    if not date_value:
        return None
    return datetime.combine(date_value.date(), time(hour=12, minute=0))


def parse_decimal(raw_value: Any) -> Optional[Decimal]:
    text = sanitize_text(raw_value)
    if not text:
        return None

    normalized = text
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            normalized = text.replace(".", "").replace(",", ".")
        else:
            normalized = text.replace(",", "")
    elif "," in text:
        normalized = text.replace(",", ".")

    try:
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def sanitize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    normalized = " ".join(str(value).split()).strip()
    return normalized or None


def build_comment_suggestion(concept: Any, observations: Any) -> Optional[str]:
    concept_text = sanitize_text(concept)
    observations_text = sanitize_text(observations)
    if concept_text and observations_text:
        return f"{concept_text} | {observations_text}"
    return concept_text or observations_text


def suggest_payment_method(movement: Any) -> Optional[str]:
    movement_text = (sanitize_text(movement) or "").lower()
    if "tarjeta" in movement_text:
        return "debit"
    if "efectivo" in movement_text:
        return "cash"
    return None


def build_fingerprint(source_bank: str, row: Dict[str, Any], amount_value: Decimal) -> str:
    parts = [
        source_bank,
        sanitize_text(row.get("F.Valor")) or "",
        sanitize_text(row.get("Fecha")) or "",
        sanitize_text(row.get("Concepto")) or "",
        sanitize_text(row.get("Movimiento")) or "",
        sanitize_text(row.get("Observaciones")) or "",
        str(abs(amount_value)),
    ]
    return sha256("|".join(parts).encode("utf-8")).hexdigest()


def normalize_bank_label(source_bank: str) -> str:
    if source_bank == "bbva":
        return "BBVA"
    if source_bank == "ing_direct":
        return "ING Direct"
    return source_bank


def to_float_or_none(value: Optional[Decimal]) -> Optional[float]:
    if value is None:
        return None
    return float(value)
