import os
from dotenv import load_dotenv

# Use a raw string for the file path or change to forward slashes
load_dotenv(r"config/.env")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "fake_details_db"
