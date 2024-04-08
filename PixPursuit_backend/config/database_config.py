"""
config/database_config.py

Configures the database connections, including both synchronous and asynchronous clients,
for MongoDB and integration with other data storage services like DigitalOcean Spaces.
"""

import motor.motor_asyncio
import time
from botocore.client import BaseClient
from pymongo import MongoClient

from config.logging_config import setup_logging
import boto3
from utils.constants import (
    MONGODB_URI, DO_REGION, DO_SPACE_ENDPOINT,
    DO_SPACE_ACCESS_KEY, DO_SPACE_SECRET_KEY
)

logger = setup_logging(__name__)


def get_mongodb_client(async_mode: bool = True):
    """
    Create a MongoDB client instance.

    :param async_mode: Flag to determine if the connection should be asynchronous.
    :return: MongoDB client instance.
    """
    if async_mode:
        return motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    else:
        return MongoClient(MONGODB_URI)


def retry_connection(connect: callable, attempts: int = 5, delay: int = 3):
    """
    Retry the database connection multiple times with a delay.

    :param connect: The connection function to call.
    :param attempts: Maximum number of attempts.
    :param delay: Delay between attempts in seconds.
    :return: Connection result or None if failed.
    """
    for attempt in range(attempts):
        try:
            return connect()
        except Exception as e:
            if attempt < attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to establish a connection: {e}")


def connect_to_mongodb(async_mode: bool = True):
    """
    Connect to MongoDB and return the database client and collections.

    :param async_mode: Flag to determine if the connection should be asynchronous.
    :return: Tuple of database client and collections.
    """
    client = retry_connection(lambda: get_mongodb_client(async_mode), attempts=5, delay=3)
    if client:
        logger.info(f"Successfully connected to MongoDB server - {'async' if async_mode else 'sync'} mode")
        return get_collections(client)
    return None, None, None, None, None


def get_collections(client):
    """
    Get the collections from MongoDB.

    :param client: MongoDB client instance.
    :return: Tuple containing MongoDB collection instances.
    """
    db = client.pixpursuit_db
    return (
        db.images,
        db.tags,
        db.faces,
        db.users,
        db.albums
    )


def connect_to_space() -> BaseClient or None:
    """
    Connect to DigitalOcean Spaces.

    :return: boto3 client instance for DigitalOcean Spaces or None if connection fails.
    """
    try:
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=DO_REGION,
                                endpoint_url=DO_SPACE_ENDPOINT,
                                aws_access_key_id=DO_SPACE_ACCESS_KEY,
                                aws_secret_access_key=DO_SPACE_SECRET_KEY)
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Digital Ocean Space: {e}")
        return None
