import logging
import os
import random
from datetime import datetime
from typing import Dict

import coloredlogs
from colorama import init
from dotenv import load_dotenv
from mimesis import Generic
from mimesis.enums import Gender, Locale
from mimesis.providers.finance import Finance
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

# Create a handler for streaming logs to the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# Add the console handler to the logger
logger = logging.getLogger("FakeDetailsGenLogs")
logger.addHandler(console_handler)

# Set up colored logs for console only
coloredlogs.install(level="INFO", logger=logger, fmt=log_format)

# Bot configuration
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
print("API_ID:", API_ID)

DB_NAME = "fake_details_db"

# Initialize the Pyrogram client
app = Client("fake_details_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize MongoDB client
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db["users"]

# Available locales
LOCALES = {
    "🇺🇸 English (US)": Locale.EN,
    "🇨🇦 English (Canada)": Locale.EN_CA,
    "🇷🇺 Russian": Locale.RU,
    "🇨🇳 Chinese": Locale.ZH,
    "🇫🇷 French": Locale.FR,
    "🇩🇪 German": Locale.DE,
    "🇪🇸 Spanish": Locale.ES,
    "🇮🇹 Italian": Locale.IT,
    "🇵🇹 Portuguese": Locale.PT,
    "🇯🇵 Japanese": Locale.JA,
    "🇰🇷 Korean": Locale.KO,
    "🇳🇱 Dutch": Locale.NL,
    "🇳🇴 Norwegian": Locale.NO,
    "🇸🇪 Swedish": Locale.SV,
    "🇩🇰 Danish": Locale.DA,
    "🇫🇮 Finnish": Locale.FI,
}

# User state storage
user_states: Dict[int, str] = {}


def get_user_logger(user_id: int) -> logging.Logger:
    user_logger = logging.getLogger(f"user_{user_id}")
    if not user_logger.handlers:
        # File handler for user-specific logs
        file_handler = logging.FileHandler(f"user_{user_id}.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        user_logger.addHandler(file_handler)

        # Ensure console logs are colored
        coloredlogs.install(level="INFO", logger=user_logger, fmt=log_format)

    user_logger.propagate = False  # Prevent double logging
    return user_logger


async def generate_details(locale: Locale) -> Dict[str, str]:
    generic = Generic(locale)
    gender = random.choice([Gender.MALE, Gender.FEMALE])
    finance_business_data_gen = Finance(locale)
    first_name = generic.person.first_name(gender=gender)
    last_name = generic.person.last_name(gender=gender)
    current_year = datetime.now().year
    age = random.randint(18, 50)
    birth_year = current_year - age
    birth_date = generic.datetime.date(start=birth_year, end=birth_year).strftime(
        "%Y-%m-%d"
    )
    details = {
        "Full Name": f"{first_name} {last_name}",
        "First Name": first_name,
        "Last Name": last_name,
        "Age": age,
        "Birth Date": birth_date,
        "Sex": generic.person.sex(),
        "University": generic.person.university(),
        "Street Name": generic.address.street_name(),
        "Street Number": generic.address.street_number(),
        "State": generic.address.state(),
        "City": generic.address.city(),
        "Country": generic.address.default_country(),
        "Postal Code": generic.address.postal_code(),
        "Company": finance_business_data_gen.company(),
        "Phone Number": generic.person.telephone(),
        "Occupation": generic.person.occupation(),
        "Nationality": generic.person.nationality(),
        "Language": generic.person.language(),
        "Username": generic.person.username(),
        "Password": generic.person.password(),
        "Weight": f"{generic.person.weight()} kg",
        "Height": f"{generic.person.height()} cm",
    }

    logger.info(
        f"Generated details for user {details['Username']} ({details['Full Name']})"
    )
    return details


async def save_details_to_db(user_id: int, username: str, details: Dict[str, str]):
    await users_collection.insert_one(
        {
            "user_id": user_id,
            "username": username,
            "details": details,
            "timestamp": datetime.now(),
        }
    )
    logger.info(f"Saved details to DB for user {username} (ID: {user_id})")


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    welcome_message = (
        f"✨<b>Hi! I'm the Faker Bot🤖</b>✨\n\n"
        f"♦️ <b>User ID:</b> {user_id}\n"
        f"♦️ <b>First Name:</b> {first_name}\n"
        f"♦️ <b>Last Name:</b> {last_name}\n\n"
        "This bot can generate fake details for various countries.\n\n"
        "<b>Commands:</b>\n"
        "♦️ /generate – Generate fake details\n"
        "♦️ /regenerate – Regenerate details for the last selected country\n"
        "♦️ /history – Show command history\n"
        "♦️ /log – Show bot log\n"
        "Type /generate to start generating fake details."
    )

    await message.reply_text(welcome_message)
    logger.info(f"Displayed start message for {username} (ID: {user_id})")


@app.on_message(filters.command("generate"))
async def generate_command(client: Client, message: Message):
    keyboard = []
    row = []
    for i, (country, locale) in enumerate(LOCALES.items()):
        row.append(
            InlineKeyboardButton(country, callback_data=f"generate_{locale.value}")
        )
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(
        "Select a country to generate fake details:", reply_markup=reply_markup
    )
    logger.info(
        f"Displayed country selection for {message.from_user.username} (ID: {message.from_user.id})"
    )


@app.on_callback_query(filters.regex(r"^generate_"))
async def generate_callback(client: Client, callback_query):
    locale_value = callback_query.data.split("_")[1]
    locale = Locale(locale_value)
    user_states[callback_query.from_user.id] = locale_value

    details = await generate_details(locale)
    user_logger = get_user_logger(callback_query.from_user.id)

    response = f"<b>Personal Profile: {details['Full Name']}</b>\n\n"
    for key, value in details.items():
        icon = (
            "👤"
            if key == "Full Name"
            else "🎂"
            if key == "Age"
            else "📅"
            if key == "Birth Date"
            else "⚧️"
            if key == "Sex"
            else "🏛️"
            if key == "University"
            else "🏠"
            if key == "Street Name"
            else "🏙️"
            if key == "City"
            else "🇺🇸"
            if key == "State"
            else "🌎"
            if key == "Country"
            else "📮"
            if key == "Postal Code"
            else "🏢"
            if key == "Company"
            else "📞"
            if key == "Phone Number"
            else "💼"
            if key == "Occupation"
            else "🌍"
            if key == "Nationality"
            else "🗣️"
            if key == "Language"
            else "🖥️"
            if key == "Username"
            else "🔐"
            if key == "Password"
            else "⚖️"
            if key == "Weight"
            else "📏"
            if key == "Height"
            else ""
        )
        response += f"{icon} <b>{key}:</b> `{value}`\n"

    await save_details_to_db(
        callback_query.from_user.id, callback_query.from_user.username, details
    )

    user_logger.info(
        f"Displayed generated details for {callback_query.from_user.username} ({callback_query.from_user.id})"
    )
    user_logger.info(
        f"Generated additional log details for {callback_query.from_user.username} ({callback_query.from_user.id})"
    )

    await callback_query.message.edit_text(response)
    logger.info(
        f"Displayed generated details for {callback_query.from_user.username} (ID: {callback_query.from_user.id})"
    )


@app.on_message(filters.command("regenerate"))
async def regenerate_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        await message.reply_text("Please use /generate first to select a country.")
        return

    locale = Locale(user_states[user_id])
    details = await generate_details(locale)
    user_logger = get_user_logger(user_id)

    response = f"<b>Personal Profile: {details['Full Name']}</b>\n\n"
    for key, value in details.items():
        icon = (
            "👤"
            if key == "Full Name"
            else "🎂"
            if key == "Age"
            else "📅"
            if key == "Birth Date"
            else "⚧️"
            if key == "Sex"
            else "🏛️"
            if key == "University"
            else "🏠"
            if key == "Street Name"
            else "🏙️"
            if key == "City"
            else "🇺🇸"
            if key == "State"
            else "🌎"
            if key == "Country"
            else "📮"
            if key == "Postal Code"
            else "🏢"
            if key == "Company"
            else "📞"
            if key == "Phone Number"
            else "💼"
            if key == "Occupation"
            else "🌍"
            if key == "Nationality"
            else "🗣️"
            if key == "Language"
            else "🖥️"
            if key == "Username"
            else "🔐"
            if key == "Password"
            else "⚖️"
            if key == "Weight"
            else "📏"
            if key == "Height"
            else ""
        )
        response += f"{icon} <b>{key}:</b> `{value}`\n"

    await save_details_to_db(user_id, message.from_user.username, details)

    user_logger.info(
        f"Displayed regenerated details for {message.from_user.username} ({message.from_user.id})"
    )
    user_logger.info(
        f"Regenerated additional log details for {message.from_user.username} ({message.from_user.id})"
    )

    await message.reply_text(response)
    logger.info(
        f"Displayed regenerated details for {message.from_user.username} (ID: {message.from_user.id})"
    )


@app.on_message(filters.command("history"))
async def history_command(client: Client, message: Message):
    user_id = message.from_user.id
    limit = 10  # Default limit

    if len(message.command) > 1:
        try:
            limit = int(message.command[1])
        except ValueError:
            await message.reply_text("Invalid limit. Using default limit of 10.")

    cursor = (
        users_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    )
    history = await cursor.to_list(length=limit)

    if not history:
        await message.reply_text("No history found.")
        return

    if len(message.command) > 1:
        response = f"<b>Last {limit} generated details:</b>\n\n"
        for entry in history:
            response += f"<b>Generated on:</b> {entry['timestamp']}\n"
            for key, value in entry["details"].items():
                icon = (
                    "👤"
                    if key == "Full Name"
                    else "🎂"
                    if key == "Age"
                    else "📅"
                    if key == "Birth Date"
                    else "⚧️"
                    if key == "Sex"
                    else "🏛️"
                    if key == "University"
                    else "🏠"
                    if key == "Street Name"
                    else "🏙️"
                    if key == "City"
                    else "🇺🇸"
                    if key == "State"
                    else "🌎"
                    if key == "Country"
                    else "📮"
                    if key == "Postal Code"
                    else "🏢"
                    if key == "Company"
                    else "📞"
                    if key == "Phone Number"
                    else "💼"
                    if key == "Occupation"
                    else "🌍"
                    if key == "Nationality"
                    else "🗣️"
                    if key == "Language"
                    else "🖥️"
                    if key == "Username"
                    else "🔐"
                    if key == "Password"
                    else "⚖️"
                    if key == "Weight"
                    else "📏"
                    if key == "Height"
                    else ""
                )
                response += f"{icon} <b>{key}:</b> {value}\n"
            response += "\n"

        await message.reply_text(response)
    else:
        html_content = "<html><body><h1>Fake Details History</h1>"
        for entry in history:
            html_content += f"<h2>Generated on: {entry['timestamp']}</h2>"
            html_content += "<ul>"
            for key, value in entry["details"].items():
                html_content += f"<li><strong>{key}:</strong> {value}</li>"
            html_content += "</ul>"
        html_content += "</body></html>"

        with open("history.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        await message.reply_document(
            "history.html", caption="Your fake details history"
        )

    logger.info(
        f"Displayed history for {message.from_user.username} (ID: {message.from_user.id})"
    )


@app.on_message(filters.command("log"))
async def log_command(client: Client, message: Message):
    user_id = message.from_user.id
    user_logger = get_user_logger(user_id)

    try:
        await message.reply_document(f"user_{user_id}.log", caption="Your log file")
    except Exception as e:
        user_logger.error(f"Error sending log file: {e}")
        await message.reply_text(
            "Error sending log file. Please check the server logs."
        )


if __name__ == "__main__":
    logger.info("Bot started")
    app.run()
