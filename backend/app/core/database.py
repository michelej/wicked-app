from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
    @staticmethod
    async def connect_db():
        Database.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print(f"Connected to MongoDB at {settings.MONGODB_URL}")
    
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
