from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.models.recurring_expense import RecurringExpense, RecurringExpenseCreate, RecurringExpenseUpdate
from app.models.transaction import TransactionCreate
from app.utils.category_references import enrich_category_reference, load_category_reference_maps, require_category_document
from app.utils.date_helpers import calculate_charge_date


class RecurringExpenseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.recurring_expenses

    async def _serialize_recurring_expense_document(self, expense: dict) -> RecurringExpense:
        category_maps = await load_category_reference_maps(self.db)
        enriched_expense = enrich_category_reference({**expense, "_id": str(expense["_id"])}, category_maps)
        return RecurringExpense(**enriched_expense)

    async def _serialize_recurring_expense_documents(self, expenses: List[dict]) -> List[RecurringExpense]:
        category_maps = await load_category_reference_maps(self.db)
        return [
            RecurringExpense(**enrich_category_reference({**expense, "_id": str(expense["_id"])}, category_maps))
            for expense in expenses
        ]
    
    async def create_recurring_expense(self, expense: RecurringExpenseCreate) -> RecurringExpense:
        """Create a new recurring expense"""
        expense_dict = expense.model_dump()
        category_document = require_category_document(
            await load_category_reference_maps(self.db),
            category_id=expense.category_id,
            category_name=expense.category,
            error_message="Category not found for recurring expense",
        )
        # Convert Decimal to float for MongoDB storage
        expense_dict["amount"] = float(expense_dict["amount"])
        expense_dict["category_id"] = category_document["_id"]
        expense_dict.pop("category", None)
        # Convert date to ISO string for MongoDB if specific_date exists
        if expense_dict.get("specific_date"):
            expense_dict["specific_date"] = expense_dict["specific_date"].isoformat()
        expense_dict["created_at"] = datetime.utcnow()
        expense_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(expense_dict)
        expense_dict["_id"] = str(result.inserted_id)
        expense_dict["category"] = category_document["name"]
        
        return RecurringExpense(**expense_dict)
    
    async def get_recurring_expense(self, expense_id: str) -> Optional[RecurringExpense]:
        """Get a recurring expense by ID"""
        expense = await self.collection.find_one({"_id": ObjectId(expense_id)})
        if expense:
            return await self._serialize_recurring_expense_document(expense)
        return None
    
    async def get_recurring_expenses(
        self,
        is_active: Optional[bool] = None,
        frequency: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RecurringExpense]:
        """Get recurring expenses with optional filters"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        if frequency:
            query["frequency"] = frequency
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("name", 1)
        expenses = []
        
        async for expense in cursor:
            expenses.append(expense)

        return await self._serialize_recurring_expense_documents(expenses)
    
    async def get_active_recurring_expenses(self) -> List[RecurringExpense]:
        """Get all active recurring expenses"""
        return await self.get_recurring_expenses(is_active=True, limit=1000)
    
    async def update_recurring_expense(
        self, 
        expense_id: str, 
        expense_update: RecurringExpenseUpdate
    ) -> Optional[RecurringExpense]:
        """Update a recurring expense"""
        update_data = {k: v for k, v in expense_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_recurring_expense(expense_id)
        
        # Convert Decimal to float if amount is being updated
        if "amount" in update_data:
            update_data["amount"] = float(update_data["amount"])

        if "category_id" in update_data or "category" in update_data:
            category_document = require_category_document(
                await load_category_reference_maps(self.db),
                category_id=update_data.get("category_id"),
                category_name=update_data.get("category"),
                error_message="Category not found for recurring expense",
            )
            update_data["category_id"] = category_document["_id"]
            update_data.pop("category", None)
        
        # Convert date to ISO string for MongoDB if specific_date is being updated
        if "specific_date" in update_data and update_data["specific_date"]:
            update_data["specific_date"] = update_data["specific_date"].isoformat()
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(expense_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            return await self._serialize_recurring_expense_document(result)
        return None
    
    async def delete_recurring_expense(self, expense_id: str) -> bool:
        """Delete a recurring expense"""
        result = await self.collection.delete_one({"_id": ObjectId(expense_id)})
        return result.deleted_count > 0
    
    def create_transactions_from_recurring(
        self,
        recurring_expenses: List[RecurringExpense],
        budget_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TransactionCreate]:
        """
        Create transaction objects from recurring expenses for a budget period.
        Returns a list of TransactionCreate objects ready to be inserted.
        """
        transactions = []
        
        for expense in recurring_expenses:
            # Calculate charge date based on frequency type
            charge_date = calculate_charge_date(
                start_date=start_date,
                end_date=end_date,
                day_of_month=expense.day_of_month,
                specific_date=expense.specific_date,
                frequency=expense.frequency
            )
            
            # Skip if charge_date is None (one-time expense outside budget period)
            if charge_date is None:
                continue
            
            transaction = TransactionCreate(
                budget_id=budget_id,
                type="expense",
                amount=expense.amount,
                category_id=expense.category_id,
                category=expense.category,
                bank=expense.bank,
                payment_method=expense.payment_method,
                comment=f"Gasto recurrente: {expense.name}",
                timestamp=charge_date,
                is_charged=False
            )
            
            transactions.append(transaction)
        
        return transactions
