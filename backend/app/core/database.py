from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
    @staticmethod
    async def connect_db():
        Database.client = AsyncIOMotorClient(settings.MONGODB_URL)
        await Database.ensure_indexes()
        print(f"Connected to MongoDB at {settings.MONGODB_URL}")

    @staticmethod
    async def ensure_indexes():
        db = Database.get_db()
        await db.budgets.create_index("start_date")
        await db.budgets.create_index("status")
        await db.transactions.create_index([("budget_id", 1), ("timestamp", -1)])
        await db.transactions.create_index([("timestamp", -1)])
        await db.transactions.create_index("category")
        await db.transactions.create_index("type")
        await db.transactions.create_index("is_charged")
        await db.recurring_expenses.create_index("is_active")
        await db.recurring_expenses.create_index("frequency")
        await db.categories.create_index("name", unique=True)
        await db.categories.create_index("type")
        await db.categories.create_index("is_active")
    
    @staticmethod
    async def close_db():
        if Database.client:
            Database.client.close()
            print("Closed MongoDB connection")
    
    @staticmethod
    def get_db():
        return Database.client[settings.MONGODB_DB_NAME]


async def get_database():
    return Database.get_db()
