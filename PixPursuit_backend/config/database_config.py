import motor.motor_asyncio
import time
from config.logging_config import setup_logging
import boto3
import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

logger = setup_logging(__name__)
load_dotenv()


def connect_to_mongodb(attempts=5, delay=3):
    for attempt in range(attempts):
        try:
            uri = os.getenv('MONGODB_URI')
            async_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            sync_client = MongoClient(uri)
            async_db = async_client.pixpursuit_db
            sync_db = sync_client.pixpursuit_db
            sync_images_collection = sync_db.images
            async_images_collection = async_db.images
            sync_tags_collection = sync_db.tags
            async_tags_collection = async_db.tags
            async_faces_collection = async_db.faces
            sync_faces_collection = sync_db.faces
            user_collection = async_db.users
            directories_collection = async_db.albums
            logger.info("Successfully connected to MongoDB server")
            return async_images_collection, sync_images_collection, async_tags_collection, sync_tags_collection, sync_faces_collection, async_faces_collection, user_collection, directories_collection

        except Exception as err:
            if attempt < attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to MongoDB server: ", err)
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
