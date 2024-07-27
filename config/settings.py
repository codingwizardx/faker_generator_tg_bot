import os

from dotenv import load_dotenv

load_dotenv("config\.env")

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "fake_details_db"
