from datetime import datetime
from typing import Dict

from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import DB_NAME, MONGO_URI

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db["users"]


async def save_details_to_db(user_id: int, username: str, details: Dict[str, str]):
    await users_collection.insert_one(
        {
            "user_id": user_id,
            "username": username,
            "details": details,
            "timestamp": datetime.now(),
        }
    )
