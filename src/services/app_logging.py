"""
Utility module providing centralized logging configuration for the Lunch Bot.

This module sets up application-wide logging with console output and rotating
log files. It is intended to be imported by other parts of the system to obtain
a correctly initialized logger instance.
"""
import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(name: str = "lunch-bot") -> logging.Logger:
    """Configure and return an application logger.

    This logger writes output to both console and a rotating log file.
    File logging is stored in `logs/lunch-bot.log` and automatically rotated.

    Args:
        name (str): Name of the logger to create or retrieve.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create logs/ directory if missing
    os.makedirs("logs", exist_ok=True)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        "logs/lunch-bot.log",
        maxBytes=1_000_000,  # 1 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
