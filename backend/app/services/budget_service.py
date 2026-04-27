from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.budget import Budget, BudgetCreate, BudgetItem, BudgetSummary, BudgetUpdate, MonthlyBudgetSummary
from app.utils.category_references import (
    CategoryReferenceMaps,
    get_parent_category_name,
    load_category_reference_maps,
    require_category_document,
    resolve_category_document,
)


class BudgetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.budgets

    async def create_budget(self, budget: BudgetCreate) -> Budget:
        """Create a new budget"""
        budget_dict = await self._prepare_budget_payload(budget.model_dump())
        budget_dict["created_at"] = datetime.utcnow()
        budget_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(budget_dict)
        return await self.get_budget(str(result.inserted_id))

    async def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get a budget by ID"""
        budget = await self.collection.find_one({"_id": ObjectId(budget_id)})
        if not budget:
            return None

        category_maps = await load_category_reference_maps(self.db)
        return self._serialize_budget_document(budget, category_maps)

    async def get_budgets(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Budget]:
        """Get all budgets with optional filters"""
        query = {}
        if status:
            query["status"] = status

        cursor = self.collection.find(query).skip(skip).limit(limit).sort("start_date", -1)
        category_maps = await load_category_reference_maps(self.db)
        budgets = []

        async for budget in cursor:
            budgets.append(self._serialize_budget_document(budget, category_maps))

        return budgets

    async def get_active_budgets(self) -> List[Budget]:
        """Get all active budgets"""
        return await self.get_budgets(status="active")

    async def update_budget(self, budget_id: str, budget_update: BudgetUpdate) -> Optional[Budget]:
        """Update a budget"""
        update_data = {key: value for key, value in budget_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_budget(budget_id)

        prepared_update_data = await self._prepare_budget_payload(update_data)
        prepared_update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(budget_id)},
            {"$set": prepared_update_data},
            return_document=True,
        )

        if not result:
            return None

        return await self.get_budget(budget_id)

    async def delete_budget(self, budget_id: str, force: bool = False) -> bool:
        """Delete a budget and optionally its related transactions."""
        if not force and await self.has_transactions(budget_id):
            return False

        if force:
            await self.db.transactions.delete_many({"budget_id": budget_id})
            await self.db.credit_card_transactions.delete_many({"budget_id": budget_id})

        result = await self.collection.delete_one({"_id": ObjectId(budget_id)})
        return result.deleted_count > 0

    async def get_budget_summary(self, budget_id: str) -> Optional[BudgetSummary]:
        """Get financial summary for a budget"""
        budget = await self.get_budget(budget_id)
        if not budget:
            return None

        category_maps = await load_category_reference_maps(self.db)
        transactions = await self._get_transactions_for_budget(self.db.transactions, budget_id)

        total_income = Decimal(0)
        total_expense = Decimal(0)
        charged_income = Decimal(0)
        charged_expense = Decimal(0)
        category_spent = self._build_category_spent_map(transactions, category_maps)

        for transaction in transactions:
            amount = Decimal(str(transaction["amount"]))

            if transaction["type"] == "income":
                total_income += amount
                if transaction.get("is_charged", False):
                    charged_income += amount
                continue

            total_expense += amount
            if transaction.get("is_charged", False):
                charged_expense += amount

        updated_items = []
        total_planned = Decimal(0)
        total_spent = Decimal(0)

        for item in budget.budget_items:
            category_name = item.category or self._resolve_category_name_from_item(item, category_maps)
            spent = category_spent.get(category_name, Decimal(0)) if category_name else Decimal(0)
            total_planned += item.planned_amount
            total_spent += spent

            updated_items.append({
                "category_id": item.category_id,
                "category": category_name,
                "planned_amount": item.planned_amount,
                "spent_amount": spent,
            })

        balance = total_income - total_expense
        charged_balance = charged_income - charged_expense
        pending_income = total_income - charged_income
        pending_expense = total_expense - charged_expense
        total_remaining = total_planned - total_spent

        return BudgetSummary(
            budget_id=budget_id,
            total_planned=total_planned,
            total_spent=total_spent,
            total_remaining=total_remaining,
            balance=balance,
            charged_balance=charged_balance,
            total_income=total_income,
            total_expense=total_expense,
            charged_income=charged_income,
            charged_expense=charged_expense,
            pending_income=pending_income,
            pending_expense=pending_expense,
            transactions_count=len(transactions),
            budget_items=updated_items,
        )

    async def has_transactions(self, budget_id: str) -> bool:
        """Check if a budget has any transactions"""
        transactions_count = await self.db.transactions.count_documents({"budget_id": budget_id}, limit=1)
        if transactions_count > 0:
            return True

        credit_card_transactions_count = await self.db.credit_card_transactions.count_documents({"budget_id": budget_id}, limit=1)
        return credit_card_transactions_count > 0

    async def recalculate_budget_items(self, budget_id: str) -> bool:
        """Recalculate spent_amount for all budget items based on transactions"""
        budget = await self.get_budget(budget_id)
        if not budget or not budget.budget_items:
            return False

        category_maps = await load_category_reference_maps(self.db)
        transactions = await self._get_transactions_for_budget(self.db.transactions, budget_id, type_filter="expense")
        category_spent = self._build_category_spent_map(transactions, category_maps)

        updated_items = []
        for item in budget.budget_items:
            category_name = item.category or self._resolve_category_name_from_item(item, category_maps)
            category_document = resolve_category_document(category_maps, category_id=item.category_id, category_name=category_name)
            spent = float(category_spent.get(category_name, Decimal(0))) if category_name else 0.0

            serialized_item: dict[str, Any] = {
                "planned_amount": float(item.planned_amount),
                "spent_amount": spent,
            }

            if category_document:
                serialized_item["category_id"] = category_document["_id"]
            elif item.category_id:
                serialized_item["category_id"] = item.category_id
            elif category_name:
                serialized_item["category"] = category_name

            updated_items.append(serialized_item)

        result = await self.collection.update_one(
            {"_id": ObjectId(budget_id)},
            {"$set": {"budget_items": updated_items, "updated_at": datetime.utcnow()}},
        )

        return result.modified_count > 0

    async def get_monthly_budget_summary(self) -> List[MonthlyBudgetSummary]:
        """Get monthly budget summaries grouped by budget_month"""

        def initialize_category_summary(summary: dict, category_name: str):
            if category_name not in summary:
                summary[category_name] = {
                    "planned": Decimal(0),
                    "spent": Decimal(0),
                    "transactions": 0,
                }

        def serialize_category_summary(summary: dict) -> dict:
            return {
                category_name: {
                    "planned": float(data["planned"]),
                    "spent": float(data["spent"]),
                    "transactions": data["transactions"],
                }
                for category_name, data in summary.items()
            }

        category_maps = await load_category_reference_maps(self.db)
        budgets = []
        cursor = self.collection.find({})
        async for budget in cursor:
            budgets.append(self._serialize_budget_document(budget, category_maps))

        monthly_groups: dict[str, List[Budget]] = {}
        for budget in budgets:
            monthly_groups.setdefault(budget.budget_month, []).append(budget)

        summaries = []
        for month, month_budgets in monthly_groups.items():
            total_planned = Decimal(0)
            total_spent = Decimal(0)
            categories_summary = {}
            credit_card_total_spent = Decimal(0)
            credit_card_transactions_count = 0
            credit_card_categories_summary = {}
            latest_start_date = max((budget.start_date for budget in month_budgets), default=datetime.min)

            for budget in month_budgets:
                for item in budget.budget_items:
                    total_planned += item.planned_amount
                    if item.category:
                        initialize_category_summary(categories_summary, item.category)
                        categories_summary[item.category]["planned"] += item.planned_amount

                budget_spent, _ = await self._aggregate_expenses(
                    "transactions",
                    str(budget.id),
                    categories_summary,
                    category_maps,
                )
                total_spent += budget_spent

                credit_spent, credit_transactions = await self._aggregate_expenses(
                    "credit_card_transactions",
                    str(budget.id),
                    credit_card_categories_summary,
                    category_maps,
                )
                credit_card_total_spent += credit_spent
                credit_card_transactions_count += credit_transactions

            summaries.append((
                latest_start_date,
                MonthlyBudgetSummary(
                    budget_month=month,
                    total_planned=total_planned,
                    total_spent=total_spent,
                    budget_count=len(month_budgets),
                    categories_summary=serialize_category_summary(categories_summary),
                    credit_card_total_spent=credit_card_total_spent,
                    credit_card_transactions_count=credit_card_transactions_count,
                    credit_card_categories_summary=serialize_category_summary(credit_card_categories_summary),
                ),
            ))

        summaries.sort(key=lambda item: item[0], reverse=True)
        return [summary for _, summary in summaries]

    async def _prepare_budget_payload(self, payload: dict) -> dict:
        prepared_payload = {**payload}

        if "budget_items" in prepared_payload:
            category_maps = await load_category_reference_maps(self.db)
            converted_items = []

            for item in prepared_payload["budget_items"]:
                category_document = require_category_document(
                    category_maps,
                    category_id=item.get("category_id"),
                    category_name=item.get("category"),
                    error_message="Category not found for budget item",
                )
                converted_items.append({
                    "category_id": category_document["_id"],
                    "planned_amount": float(item["planned_amount"]),
                    "spent_amount": float(item.get("spent_amount", 0)),
                })

            prepared_payload["budget_items"] = converted_items

        planning_metadata = prepared_payload.get("planning_metadata")
        if planning_metadata and "temporary_incomes" in planning_metadata:
            prepared_payload["planning_metadata"] = {
                **planning_metadata,
                "temporary_incomes": [
                    {
                        "label": item["label"],
                        "amount": float(item["amount"]),
                    }
                    for item in planning_metadata.get("temporary_incomes", [])
                ],
            }

        return prepared_payload

    def _serialize_budget_document(self, budget: dict, category_maps: CategoryReferenceMaps) -> Budget:
        serialized_budget = {**budget, "_id": str(budget["_id"])}
        serialized_budget["budget_items"] = self._serialize_budget_items(serialized_budget.get("budget_items", []), category_maps)
        return Budget(**serialized_budget)

    def _serialize_budget_items(self, budget_items: list, category_maps: CategoryReferenceMaps) -> List[dict]:
        serialized_items = []

        for raw_item in budget_items:
            item_dict = raw_item.model_dump() if hasattr(raw_item, "model_dump") else dict(raw_item)
            category_document = resolve_category_document(
                category_maps,
                category_id=item_dict.get("category_id"),
                category_name=item_dict.get("category"),
            )

            serialized_items.append({
                "category_id": category_document["_id"] if category_document else item_dict.get("category_id"),
                "category": category_document["name"] if category_document else item_dict.get("category"),
                "planned_amount": item_dict.get("planned_amount", 0),
                "spent_amount": item_dict.get("spent_amount", 0),
            })

        return serialized_items

    def _resolve_category_name_from_item(self, item: BudgetItem, category_maps: CategoryReferenceMaps) -> Optional[str]:
        category_document = resolve_category_document(category_maps, category_id=item.category_id, category_name=item.category)
        if category_document:
            return category_document["name"]

        return item.category

    def _resolve_category_name_from_document(self, document: dict, category_maps: CategoryReferenceMaps) -> Optional[str]:
        category_document = resolve_category_document(
            category_maps,
            category_id=document.get("category_id"),
            category_name=document.get("category"),
        )
        if category_document:
            return category_document["name"]

        return document.get("category")

    def _build_category_spent_map(self, transactions: List[dict], category_maps: CategoryReferenceMaps) -> dict[str, Decimal]:
        category_spent: dict[str, Decimal] = {}

        for transaction in transactions:
            category_name = self._resolve_category_name_from_document(transaction, category_maps)
            if not category_name:
                continue

            amount = Decimal(str(transaction["amount"]))
            category_spent[category_name] = category_spent.get(category_name, Decimal(0)) + amount

            parent_name = get_parent_category_name(
                category_maps,
                category_id=transaction.get("category_id"),
                category_name=category_name,
            )
            if parent_name:
                category_spent[parent_name] = category_spent.get(parent_name, Decimal(0)) + amount

        return category_spent

    async def _get_transactions_for_budget(
        self,
        collection,
        budget_id: str,
        type_filter: Optional[str] = None,
    ) -> List[dict]:
        query: dict[str, Any] = {"budget_id": budget_id}
        if type_filter:
            query["type"] = type_filter

        cursor = collection.find(query)
        transactions = []
        async for transaction in cursor:
            transactions.append(transaction)
        return transactions

    async def _aggregate_expenses(
        self,
        collection_name: str,
        budget_id: str,
        target_summary: dict,
        category_maps: CategoryReferenceMaps,
    ) -> tuple[Decimal, int]:
        collection = self.db[collection_name]
        cursor = collection.find({"budget_id": budget_id, "type": "expense"})
        total_amount = Decimal(0)
        transaction_count = 0

        async for transaction in cursor:
            category_name = self._resolve_category_name_from_document(transaction, category_maps)
            if not category_name or category_name == "Transferido Cuentas":
                continue

            amount = Decimal(str(transaction["amount"]))
            target_summary.setdefault(category_name, {"planned": Decimal(0), "spent": Decimal(0), "transactions": 0})
            target_summary[category_name]["spent"] += amount
            target_summary[category_name]["transactions"] += 1

            parent_name = get_parent_category_name(
                category_maps,
                category_id=transaction.get("category_id"),
                category_name=category_name,
            )
            if parent_name:
                target_summary.setdefault(parent_name, {"planned": Decimal(0), "spent": Decimal(0), "transactions": 0})
                target_summary[parent_name]["spent"] += amount
                target_summary[parent_name]["transactions"] += 1

            total_amount += amount
            transaction_count += 1

        return total_amount, transaction_count
