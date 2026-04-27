from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Dict, Any
from decimal import Decimal
from collections import defaultdict
from app.utils.date_helpers import get_date_range
from app.utils.category_references import load_category_reference_maps, resolve_category_document


class DashboardService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_daily_progress(self, budget_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get day-by-day financial progress for a budget.
        Returns cumulative balance for each day.
        """
        # Get all charged transactions for this budget
        transactions = []
        cursor = self.db.transactions.find({
            "budget_id": budget_id,
            "is_charged": True,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", 1)
        
        async for trans in cursor:
            transactions.append(trans)
        
        # Generate all dates in range
        date_range = get_date_range(start_date, end_date)
        
        # Group transactions by date
        daily_transactions = defaultdict(list)
        for trans in transactions:
            date_key = trans["timestamp"].replace(hour=0, minute=0, second=0, microsecond=0)
            daily_transactions[date_key].append(trans)
        
        # Calculate cumulative balance day by day
        daily_data = []
        current_balance = Decimal(0)
        
        for date in date_range:
            day_transactions = daily_transactions.get(date, [])
            
            day_income = sum(Decimal(str(t["amount"])) for t in day_transactions if t["type"] == "income")
            day_expense = sum(Decimal(str(t["amount"])) for t in day_transactions if t["type"] == "expense")
            
            current_balance += (day_income - day_expense)
            
            daily_data.append({
                "date": date.isoformat(),
                "income": float(day_income),
                "expense": float(day_expense),
                "balance": float(current_balance),
                "transactions_count": len(day_transactions)
            })
        
        return daily_data
    
    async def get_category_summary(self, budget_id: str) -> List[Dict[str, Any]]:
        """
        Get expense summary grouped by category for a budget.
        """
        category_maps = await load_category_reference_maps(self.db)
        pipeline = [
            {"$match": {"budget_id": budget_id, "type": "expense"}},
            {"$group": {
                "_id": {
                    "category_id": "$category_id",
                    "category": "$category",
                },
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
                "charged": {"$sum": {"$cond": ["$is_charged", "$amount", 0]}},
                "pending": {"$sum": {"$cond": ["$is_charged", 0, "$amount"]}}
            }},
            {"$sort": {"total": -1}}
        ]
        
        results = []
        async for result in self.db.transactions.aggregate(pipeline):
            category_document = resolve_category_document(
                category_maps,
                category_id=result["_id"].get("category_id"),
                category_name=result["_id"].get("category"),
            )
            results.append({
                "category_id": category_document["_id"] if category_document else result["_id"].get("category_id"),
                "category": category_document["name"] if category_document else result["_id"].get("category"),
                "total": float(result["total"]),
                "count": result["count"],
                "charged": float(result["charged"]),
                "pending": float(result["pending"])
            })
        
        return results
    
    async def get_payment_method_summary(self, budget_id: str) -> List[Dict[str, Any]]:
        """
        Get expense summary grouped by payment method.
        """
        pipeline = [
            {"$match": {"budget_id": budget_id}},
            {"$group": {
                "_id": {
                    "payment_method": "$payment_method",
                    "type": "$type"
                },
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total": -1}}
        ]
        
        results = []
        async for result in self.db.transactions.aggregate(pipeline):
            results.append({
                "payment_method": result["_id"]["payment_method"],
                "type": result["_id"]["type"],
                "total": float(result["total"]),
                "count": result["count"]
            })
        
        return results
    
    async def get_upcoming_recurring_expenses(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get recurring expenses that are due in the next X days.
        """
        now = datetime.utcnow()
        current_day = now.day
        category_maps = await load_category_reference_maps(self.db)
        
        # Get all active recurring expenses
        cursor = self.db.recurring_expenses.find({"is_active": True})
        upcoming = []
        
        async for expense in cursor:
            day_of_month = expense["day_of_month"]
            
            # Simple calculation: if day is coming up this month
            if day_of_month >= current_day and day_of_month <= (current_day + days_ahead):
                days_until = day_of_month - current_day
                category_document = resolve_category_document(
                    category_maps,
                    category_id=expense.get("category_id"),
                    category_name=expense.get("category"),
                )
                upcoming.append({
                    "id": str(expense["_id"]),
                    "name": expense["name"],
                    "category_id": category_document["_id"] if category_document else expense.get("category_id"),
                    "category": category_document["name"] if category_document else expense.get("category"),
                    "amount": float(expense["amount"]),
                    "day_of_month": day_of_month,
                    "days_until": days_until,
                    "payment_method": expense["payment_method"],
                    "bank": expense.get("bank")
                })
        
        # Sort by days until due
        upcoming.sort(key=lambda x: x["days_until"])
        
        return upcoming
    
    async def get_budget_comparison(self, budget_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Compare financial summaries across multiple budgets.
        """
        comparisons = []
        
        for budget_id in budget_ids:
            # Get budget info
            budget = await self.db.budgets.find_one({"_id": budget_id})
            if not budget:
                continue
            
            # Get transactions summary
            pipeline = [
                {"$match": {"budget_id": budget_id}},
                {"$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"},
                    "charged": {"$sum": {"$cond": ["$is_charged", "$amount", 0]}},
                    "count": {"$sum": 1}
                }}
            ]
            
            income_data = {"total": 0, "charged": 0, "count": 0}
            expense_data = {"total": 0, "charged": 0, "count": 0}
            
            async for result in self.db.transactions.aggregate(pipeline):
                if result["_id"] == "income":
                    income_data = result
                elif result["_id"] == "expense":
                    expense_data = result
            
            comparisons.append({
                "budget_id": str(budget["_id"]),
                "budget_name": budget["name"],
                "start_date": budget["start_date"].isoformat(),
                "end_date": budget["end_date"].isoformat(),
                "total_income": float(income_data.get("total", 0)),
                "total_expense": float(expense_data.get("total", 0)),
                "balance": float(income_data.get("total", 0) - expense_data.get("total", 0)),
                "transactions_count": income_data.get("count", 0) + expense_data.get("count", 0)
            })
        
        return comparisons
