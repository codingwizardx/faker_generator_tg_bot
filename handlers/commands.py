from mimesis.enums import Locale
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config.settings import API_HASH, API_ID, BOT_TOKEN
from logs.logger import get_user_logger, logger
from utils.database import save_details_to_db, users_collection
from utils.details_generator import generate_details

app = Client("fake_details_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_states = {}

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
async def generate_callback(client: Client, callback_query: CallbackQuery):
    try:
        locale_value = callback_query.data.split("_")[1]
        locale = Locale(locale_value)
        user_states[callback_query.from_user.id] = locale_value

        # Logging for debugging
        logger.info(f"Generating details for locale: {locale_value}")
        user_logger = get_user_logger(callback_query.from_user.id)
        user_logger.info(f"Generating details for locale: {locale_value}")

        details = await generate_details(locale)

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

        # Answer the callback query
        await callback_query.answer()
        await callback_query.message.edit_text(response)
        logger.info(
            f"Displayed generated details for {callback_query.from_user.username} (ID: {callback_query.from_user.id})"
        )
    except Exception as e:
        logger.error(f"Error in generate_callback: {e}")
        user_logger.error(f"Error in generate_callback: {e}")
        await callback_query.answer(
            "An error occurred. Please try again.", show_alert=True
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
