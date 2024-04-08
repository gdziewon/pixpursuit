"""
data/databases/mongodb/sync/celery_database_tools.py

Contains utility functions for interacting with the database within Celery tasks. This includes
adding data to images, retrieving image documents synchronously, paginating image IDs, and managing
tags and feedback for images.
"""

from bson import ObjectId
from tenacity import retry, stop_after_attempt, wait_fixed
from config.logging_config import setup_logging
from config.database_config import connect_to_mongodb
from utils.function_utils import to_object_id

logger = setup_logging(__name__)

sync_images_collection, sync_tags_collection, sync_faces_collection, _, _ = connect_to_mongodb(async_mode=False)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_field_to_image(field_to_set: str, data: any, filename: str) -> None:
    """
    Adds specified data to a field in an image document identified by filename.

    :param field_to_set: The field name in the document where data should be set.
    :param data: The data to add to the field.
    :param filename: The filename identifying the image document.
    """
    try:
        sync_images_collection.update_one(
            {'filename': filename},
            {'$set': {field_to_set: data}}
        )
    except Exception as e:
        logger.error(f"Error adding {field_to_set} to image: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_image_document_sync(inserted_id: ObjectId or str) -> dict or None:
    """
    Retrieves an image document synchronously by its ID.

    :param inserted_id: The ID of the image document to retrieve.
    :return: The image document as a dictionary if found, otherwise None.
    """
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return None

    try:
        return sync_images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_image_ids_paginated(last_id: ObjectId or str = None, page_size: int = 100) -> list[str]:
    """
    Retrieves a paginated list of image document IDs.

    :param last_id: The last ID retrieved, used for pagination.
    :param page_size: The number of document IDs to retrieve per page.
    :return: A list of image document IDs.
    """
    if last_id is not None:
        last_id = to_object_id(last_id)
        cursor = sync_images_collection.find({'_id': {'$gt': last_id}}, {'_id': 1}).limit(page_size)
    else:
        cursor = sync_images_collection.find({}, {'_id': 1}).limit(page_size)

    return [str(document['_id']) for document in cursor]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_unique_tags() -> list[str] or None:
    """
    Retrieves a list of unique tags from the tags collection.

    :return: A list of unique tag names or None if an error occurs.
    """
    documents = sync_tags_collection.find({}, {'name': 1})
    names = [doc['name'] for doc in documents]
    return names


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_auto_tags(inserted_id: ObjectId or str, predicted_tags: list[str]) -> None:
    """
    Adds automatically predicted tags to an image document.

    :param inserted_id: The ID of the image document to update.
    :param predicted_tags: A list of tags predicted by the model.
    """
    try:
        image_document = get_image_document_sync(inserted_id)
        if not image_document:
            logger.error(f"No document found with id: {str(inserted_id)}")
            return

        # Filter out tags that are already marked by the user
        user_tags = image_document.get('user_tags', [])
        auto_tags_to_add = [tag for tag in predicted_tags if tag not in user_tags]

        # Update the document with the new automatic tags if there are any to add
        if auto_tags_to_add:
            inserted_id = to_object_id(inserted_id)
            sync_images_collection.update_one(
                {'_id': inserted_id},
                {'$set': {'auto_tags': auto_tags_to_add}}
            )
            # Add feedback entry for new tags
            add_feedback_sync(auto_tags_to_add, inserted_id)

    except Exception as e:
        logger.error(f"Error while adding auto tags: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_feedback_sync(auto_tags: list[str], inserted_id: ObjectId or str) -> bool:
    """
    Adds feedback entries for automatically generated tags in the image document.

    :param auto_tags: A list of tags to add feedback for.
    :param inserted_id: The ID of the image document to update.
    :return: True if feedback was successfully added, False otherwise.
    """
    try:
        image_document = get_image_document_sync(inserted_id)
        existing_feedback = image_document.get('feedback', {})
        for tag in auto_tags:
            existing_feedback.setdefault(tag, {"positive": 0, "negative": 0})

        existing_feedback = {tag: data for tag, data in existing_feedback.items() if tag in auto_tags}

        sync_images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'feedback': existing_feedback}}
        )

        return True
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False
