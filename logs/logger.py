import logging

from colorama import init

init(autoreset=True)

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure general logger
logger = logging.getLogger("FakeDetailsGenLogs")
logger.setLevel(logging.INFO)

# Console handler with colorized output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)


def get_user_logger(user_id: int) -> logging.Logger:
    user_logger = logging.getLogger(f"user_{user_id}")
    if not user_logger.handlers:
        # File handler for user-specific logs
        file_handler = logging.FileHandler(f"logs/user_{user_id}.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        user_logger.addHandler(file_handler)

    user_logger.propagate = False  # Prevent double logging
    return user_logger
