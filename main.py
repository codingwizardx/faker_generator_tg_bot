from handlers.commands import app
from logs.logger import logger

if __name__ == "__main__":
    logger.info("Bot started")
    app.run()
