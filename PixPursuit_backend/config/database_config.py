import motor.motor_asyncio
import time
from config.logging_config import setup_logging
import boto3
import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

logger = setup_logging(__name__)
load_dotenv()

URI = os.getenv('MONGODB_URI')


def connect_to_mongodb_async(attempts=5, delay=3):
    for attempt in range(attempts):
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(URI)
            collections = get_collections(client)
            logger.info("Successfully connected to MongoDB server - async mode")
            return collections

        except Exception as err:
            if attempt < attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to MongoDB server: ", err)
                return None, None, None, None, None


def connect_to_mongodb_sync(attempts=5, delay=3):
    for attempt in range(attempts):
        try:
            client = MongoClient(URI)
            collections = get_collections(client)
            logger.info("Successfully connected to MongoDB server - sync mode")
            return collections

        except Exception as err:
            if attempt < attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to MongoDB server: ", err)
                return None, None, None, None, None


def get_collections(client):
    if client:
        db = client.pixpursuit_db
        images_collection = db.images
        tags_collection = db.tags
        faces_collection = db.faces
        user_collection = db.users
        directories_collection = db.albums
        return images_collection, tags_collection, faces_collection, user_collection, directories_collection
    else:
        return None, None, None, None, None


def connect_to_space():
    try:
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name='ams3',
                                endpoint_url=os.getenv('DO_SPACE_ENDPOINT'),
                                aws_access_key_id=os.getenv('DO_SPACE_ACCESS_KEY'),
                                aws_secret_access_key=os.getenv('DO_SPACE_SECRET_KEY'))
    except Exception as e:
        logger.error(f"Failed to connect to Digital Ocean Space: {e}")
        return None
    return client
