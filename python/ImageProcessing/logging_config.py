import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=1)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[handler])
