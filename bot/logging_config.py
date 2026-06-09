"""Logging configuration for the trading bot."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOGGER_NAME = "trading_bot"
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class InfoOnlyFilter(logging.Filter):
    """Allow only INFO records through a handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == logging.INFO


def setup_logging() -> logging.Logger:
    """Configure console and rotating file logging for the application."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(InfoOnlyFilter())
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
