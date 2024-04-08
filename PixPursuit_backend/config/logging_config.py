"""
config/logging_config.py

Establishes the logging configuration used across the application, setting up log file
rotation, format, and log level. This module centralizes logging setup to ensure consistent
logging behavior.
"""

import logging
from logging.handlers import RotatingFileHandler
from utils.constants import LOG_FILE_PATH, LOG_FORMAT


def setup_logging(name: str) -> logging.Logger:
    """
    Configure and return a logger with a rotating file handler.

    :param name: Name of the logger to configure.
    :return: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Check if the logger already has handlers
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=1000000000,  # 1GB
            backupCount=5
        )
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
