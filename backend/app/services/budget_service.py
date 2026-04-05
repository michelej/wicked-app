from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from app.models.budget import Budget, BudgetCreate, BudgetUpdate, BudgetSummary, MonthlyBudgetSummary


class BudgetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.budgets
    
    async def create_budget(self, budget: BudgetCreate) -> Budget:
        """Create a new budget"""
        budget_dict = budget.model_dump()
        
        # Convert budget_items Decimals to floats for MongoDB
        if "budget_items" in budget_dict:
            converted_items = []
            for item in budget_dict["budget_items"]:
                converted_items.append({
                    "category": item["category"],
                    "planned_amount": float(item["planned_amount"]),
                    "spent_amount": float(item.get("spent_amount", 0))
                })
            budget_dict["budget_items"] = converted_items
        
        budget_dict["created_at"] = datetime.utcnow()
        budget_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(budget_dict)
        budget_dict["_id"] = str(result.inserted_id)
        
        return Budget(**budget_dict)
    
    async def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get a budget by ID"""
        budget = await self.collection.find_one({"_id": ObjectId(budget_id)})
        if budget:
            budget["_id"] = str(budget["_id"])
            return Budget(**budget)
        return None
    
    async def get_budgets(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Budget]:
        """Get all budgets with optional filters"""
        query = {}
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("start_date", -1)
        budgets = []
        
        async for budget in cursor:
            budget["_id"] = str(budget["_id"])
            budgets.append(Budget(**budget))
        
        return budgets
    
    async def get_active_budgets(self) -> List[Budget]:
        """Get all active budgets"""
        return await self.get_budgets(status="active")
    
    async def update_budget(self, budget_id: str, budget_update: BudgetUpdate) -> Optional[Budget]:
        """Update a budget"""
        update_data = {k: v for k, v in budget_update.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await self.get_budget(budget_id)
        
        # Convert budget_items Decimals to floats for MongoDB
        if "budget_items" in update_data:
            converted_items = []
            for item in update_data["budget_items"]:
                converted_items.append({
                    "category": item["category"],
                    "planned_amount": float(item["planned_amount"]),
                    "spent_amount": float(item.get("spent_amount", 0))
                })
            update_data["budget_items"] = converted_items
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(budget_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            return Budget(**result)
        return None
    
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget"""
        result = await self.collection.delete_one({"_id": ObjectId(budget_id)})
        return result.deleted_count > 0
    
    async def get_budget_summary(self, budget_id: str) -> Optional[BudgetSummary]:
        """Get financial summary for a budget"""
        # Get budget with items
        budget = await self.get_budget(budget_id)
        if not budget:
            return None
        
        # Get all categories to build parent-child relationship map
        # Maps category_name -> parent_name (since we store names, not IDs)
        category_to_parent = {}  # Maps child name -> parent name
        categories_by_name = {}  # Maps name -> full category doc
        categories_by_id = {}    # Maps id -> full category doc
        
        cursor = self.db.categories.find({})
        async for cat in cursor:
            cat_id = str(cat["_id"])
            cat_name = cat["name"]
            categories_by_id[cat_id] = cat
            categories_by_name[cat_name] = cat
        
        # Build the parent mapping: child_name -> parent_name
        for cat_name, cat in categories_by_name.items():
            if cat.get("parent_id"):
                parent_id = cat["parent_id"]
                if parent_id in categories_by_id:
                    parent_name = categories_by_id[parent_id]["name"]
                    category_to_parent[cat_name] = parent_name
        
        # Get all transactions for this budget
        transactions = []
        cursor = self.db.transactions.find({"budget_id": budget_id})
        
        async for trans in cursor:
            transactions.append(trans)
        
        # Calculate totals
        total_income = Decimal(0)
        total_expense = Decimal(0)
        charged_income = Decimal(0)
        charged_expense = Decimal(0)
        
        # Calculate spent amount by category
        category_spent = {}
        
        for trans in transactions:
            amount = Decimal(str(trans["amount"]))
            
            if trans["type"] == "income":
                total_income += amount
                if trans.get("is_charged", False):
                    charged_income += amount
            else:  # expense
                total_expense += amount
                if trans.get("is_charged", False):
                    charged_expense += amount
                
                # Track spending by category (including parent categories)
                category_name = trans["category"]  # This is the category NAME, not ID
                
                # Add to the direct category
                if category_name not in category_spent:
                    category_spent[category_name] = Decimal(0)
                category_spent[category_name] += amount
                
                # If this category has a parent, also add to parent's spent amount
                if category_name in category_to_parent:
                    parent_name = category_to_parent[category_name]
                    if parent_name not in category_spent:
                        category_spent[parent_name] = Decimal(0)
                    category_spent[parent_name] += amount
        
        # Update budget items with actual spent amounts
        updated_items = []
        total_planned = Decimal(0)
        total_spent = Decimal(0)
        
        for item in budget.budget_items:
            spent = category_spent.get(item.category, Decimal(0))
            total_planned += item.planned_amount
            total_spent += spent
            
            updated_items.append({
                "category": item.category,
                "planned_amount": item.planned_amount,
                "spent_amount": spent
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
            budget_items=updated_items
        )
    
    async def has_transactions(self, budget_id: str) -> bool:
        """Check if a budget has any transactions"""
        count = await self.db.transactions.count_documents({"budget_id": budget_id})
        return count > 0
    
    async def recalculate_budget_items(self, budget_id: str) -> bool:
        """Recalculate spent_amount for all budget items based on transactions"""
        budget = await self.get_budget(budget_id)
        if not budget or not budget.budget_items:
            return False
        
        # Get all categories to build parent-child relationship map
        # Maps category_name -> parent_name (since we store names, not IDs)
        category_to_parent = {}  # Maps child name -> parent name
        categories_by_name = {}  # Maps name -> full category doc
        categories_by_id = {}    # Maps id -> full category doc
        
        cursor = self.db.categories.find({})
        async for cat in cursor:
            cat_id = str(cat["_id"])
            cat_name = cat["name"]
            categories_by_id[cat_id] = cat
            categories_by_name[cat_name] = cat
        
        # Build the parent mapping: child_name -> parent_name
        for cat_name, cat in categories_by_name.items():
            if cat.get("parent_id"):
                parent_id = cat["parent_id"]
                if parent_id in categories_by_id:
                    parent_name = categories_by_id[parent_id]["name"]
                    category_to_parent[cat_name] = parent_name
        
        # Get all expense transactions for this budget
        transactions = []
        cursor = self.db.transactions.find({"budget_id": budget_id, "type": "expense"})
        
        async for trans in cursor:
            transactions.append(trans)
        
        # Calculate spent amount by category
        # This will include both direct spending and child category spending
        category_spent = {}
        for trans in transactions:
            category_name = trans["category"]  # This is the category NAME, not ID
            amount = Decimal(str(trans["amount"]))
            
            # Add to the direct category
            if category_name not in category_spent:
                category_spent[category_name] = Decimal(0)
            category_spent[category_name] += amount
            
            # If this category has a parent, also add to parent's spent amount
            if category_name in category_to_parent:
                parent_name = category_to_parent[category_name]
                if parent_name not in category_spent:
                    category_spent[parent_name] = Decimal(0)
                category_spent[parent_name] += amount
        
        # Update budget items
        updated_items = []
        for item in budget.budget_items:
            spent = float(category_spent.get(item.category, Decimal(0)))
            updated_items.append({
                "category": item.category,
                "planned_amount": float(item.planned_amount),
                "spent_amount": spent
            })
        
        # Update budget in database
        result = await self.collection.update_one(
            {"_id": ObjectId(budget_id)},
            {"$set": {"budget_items": updated_items, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_monthly_budget_summary(self) -> List[MonthlyBudgetSummary]:
        """Get monthly budget summaries grouped by budget_month"""

        def initialize_category_summary(summary: dict, category_name: str):
            if category_name not in summary:
                summary[category_name] = {
                    "planned": Decimal(0),
                    "spent": Decimal(0),
                    "transactions": 0
                }

        async def aggregate_expenses(collection_name: str, budget_id: str, target_summary: dict) -> tuple[Decimal, int]:
            collection = self.db[collection_name]
            cursor = collection.find({"budget_id": budget_id, "type": "expense"})
            total_amount = Decimal(0)
            transaction_count = 0

            async for trans in cursor:
                category_name = trans["category"]
                amount = Decimal(str(trans["amount"]))

                if category_name == "Transferido Cuentas":
                    continue

                initialize_category_summary(target_summary, category_name)
                target_summary[category_name]["spent"] += amount
                target_summary[category_name]["transactions"] += 1

                if category_name in category_to_parent:
                    parent_name = category_to_parent[category_name]
                    initialize_category_summary(target_summary, parent_name)
                    target_summary[parent_name]["spent"] += amount
                    target_summary[parent_name]["transactions"] += 1

                total_amount += amount
                transaction_count += 1

            return total_amount, transaction_count

        def serialize_category_summary(summary: dict) -> dict:
            converted_summary = {}
            for cat_name, data in summary.items():
                converted_summary[cat_name] = {
                    "planned": float(data["planned"]),
                    "spent": float(data["spent"]),
                    "transactions": data["transactions"]
                }

            return converted_summary
        
        # Get all budgets
        budgets = []
        cursor = self.collection.find({})
        async for budget in cursor:
            budget["_id"] = str(budget["_id"])
            budgets.append(Budget(**budget))
        
        # Group budgets by budget_month
        monthly_groups = {}
        for budget in budgets:
            month = budget.budget_month
            if month not in monthly_groups:
                monthly_groups[month] = []
            monthly_groups[month].append(budget)
        
        # Calculate summaries for each month
        summaries = []
        for month, month_budgets in monthly_groups.items():
            total_planned = Decimal(0)
            total_spent = Decimal(0)
            categories_summary = {}
            credit_card_total_spent = Decimal(0)
            credit_card_transactions_count = 0
            credit_card_categories_summary = {}
            latest_start_date = max((budget.start_date for budget in month_budgets), default=datetime.min)
            
            # Get all categories to build parent-child relationship map
            category_to_parent = {}
            categories_by_name = {}
            categories_by_id = {}
            
            cursor = self.db.categories.find({})
            async for cat in cursor:
                cat_id = str(cat["_id"])
                cat_name = cat["name"]
                categories_by_id[cat_id] = cat
                categories_by_name[cat_name] = cat
            
            # Build the parent mapping
            for cat_name, cat in categories_by_name.items():
                if cat.get("parent_id"):
                    parent_id = cat["parent_id"]
                    if parent_id in categories_by_id:
                        parent_name = categories_by_id[parent_id]["name"]
                        category_to_parent[cat_name] = parent_name
            
            # Process each budget in the month
            for budget in month_budgets:
                # Add planned amounts
                for item in budget.budget_items:
                    total_planned += item.planned_amount

                budget_spent, _ = await aggregate_expenses("transactions", str(budget.id), categories_summary)
                total_spent += budget_spent

                credit_spent, credit_transactions = await aggregate_expenses(
                    "credit_card_transactions",
                    str(budget.id),
                    credit_card_categories_summary
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
                    credit_card_categories_summary=serialize_category_summary(credit_card_categories_summary)
                )
            ))
        
        summaries.sort(key=lambda x: x[0], reverse=True)
        
        return [summary for _, summary in summaries]
