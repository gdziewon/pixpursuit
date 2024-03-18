from bson import ObjectId
from tenacity import retry, stop_after_attempt, wait_fixed
from config.logging_config import setup_logging
from config.database_config import connect_to_mongodb_sync
from utils.function_utils import to_object_id

logger = setup_logging(__name__)

sync_images_collection, sync_tags_collection, sync_faces_collection, _, _ = connect_to_mongodb_sync()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_something_to_image(field_to_set: str, data: any, filename: str) -> None:
    try:
        sync_images_collection.update_one(
            {'filename': filename},
            {'$set': {field_to_set: data}}
        )
    except Exception as e:
        logger.error(f"Error adding {field_to_set} to image: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_image_document_sync(inserted_id: ObjectId or str) -> dict or None:
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
    if last_id is not None:
        last_id = to_object_id(last_id)
        cursor = sync_images_collection.find({'_id': {'$gt': last_id}}, {'_id': 1}).limit(page_size)
    else:
        cursor = sync_images_collection.find({}, {'_id': 1}).limit(page_size)

    return [str(document['_id']) for document in cursor]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_unique_tags() -> list[str] or None:
    documents = sync_tags_collection.find({}, {'name': 1})
    names = [doc['name'] for doc in documents]
    return names


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_auto_tags(inserted_id: ObjectId or str, predicted_tags: list[str]) -> None:
    try:
        image_document = get_image_document_sync(inserted_id)
        if not image_document:
            logger.error(f"No document found with id: {str(inserted_id)}")
            return

        user_tags = image_document.get('user_tags', [])
        auto_tags_to_add = [tag for tag in predicted_tags if tag not in user_tags]

        if auto_tags_to_add:
            inserted_id = to_object_id(inserted_id)
            sync_images_collection.update_one(
                {'_id': inserted_id},
                {'$set': {'auto_tags': auto_tags_to_add}}
            )
            add_feedback_sync(auto_tags_to_add, inserted_id)

    except Exception as e:
        logger.error(f"Error while adding auto tags: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_feedback_sync(auto_tags: list[str], inserted_id: ObjectId or str) -> bool:
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
