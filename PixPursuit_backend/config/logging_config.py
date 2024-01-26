import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, '..', 'generated', 'app.log')

    handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
