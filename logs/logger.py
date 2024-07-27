import logging
from colorama import init
import os

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

def setup_logger(user_id: int):
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file_path = f"{log_directory}/user_{user_id}.log"
    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    user_logger = logging.getLogger(f"user_{user_id}")
    if not user_logger.handlers:
        user_logger.addHandler(file_handler)
    user_logger.propagate = False  # Prevent double logging


def get_user_logger(user_id: int) -> logging.Logger:
    return logging.getLogger(f"user_{user_id}")
