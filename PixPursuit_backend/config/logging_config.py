import logging
from logging.handlers import RotatingFileHandler
from utils.constants import LOG_FILE_PATH, LOG_FORMAT


def setup_logging(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_file_path = LOG_FILE_PATH

    handler = RotatingFileHandler(log_file_path, maxBytes=1000000000, backupCount=5)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
