import logging
import os
from logging.handlers import RotatingFileHandler
from utils.function_utils import get_generated_dir_path


def setup_logging(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_file_path = os.path.join(get_generated_dir_path(), 'app.log')

    handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
