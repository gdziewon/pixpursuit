from setup import connect_to_mongodb
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

images_collection, tags_collection, user_collection = connect_to_mongodb()


async def save_to_database(data, username):
    try:
        face_embeddings, detected_objects, image_url, thumbnail_url, exif_data, features = data
        embeddings_list = [emb.tolist() for emb in face_embeddings] if face_embeddings is not None else []
        features_list = features.tolist() if features is not None else []

        image_record = {
            'image_url': image_url,
            'thumbnail_url': thumbnail_url,
            'embeddings': embeddings_list,
            'detected_objects': detected_objects,
            'metadata': exif_data,
            'features': features_list,
            'user_tags': [],
            'auto_tags': [],
            'feedback': {},
            'description': "",
            'added_by': username
        }
        logger.info(f"Successfully saved data for image: {image_url}")
        result = await images_collection.insert_one(image_record)
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return None


async def add_tags(tags, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            {'$addToSet': {'user_tags': {'$each': tags}}}
        )
        if update_result.matched_count == 0:
            return False

        for tag in tags:
            if not await tags_collection.find_one({'name': tag}):
                await tags_collection.insert_one({'name': tag})

        return True
    except Exception as e:
        logger.error(f"Error in add_tags: {e}")
        return False


async def add_feedback(feedback, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)

        update_operations = {'$set': {f'feedback.{tag}': value for tag, value in feedback.items() if value is not False},
                             '$setOnInsert': {f'feedback.{tag}': False for tag, value in feedback.items() if value is False}}

        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            update_operations,
            upsert=True
        )

        logger.info(f"Successfully added feedback")
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False


async def add_description(description, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'description': description}}
        )
        logger.info("Successfully added description")
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating description: {e}")
        return False


async def add_auto_tags(inserted_id, predicted_tags):
    try:
        image_document = await get_image_document(inserted_id)
        user_tags = image_document.get('user_tags', [])
        feedback = image_document.get('feedback', {})
        filtered_predicted_tags = [tag for tag in predicted_tags if tag not in user_tags]
        await images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'auto_tags': predicted_tags}}
            )
        feedback_update = {tag: feedback.get(tag, False) for tag in filtered_predicted_tags}
        await add_feedback(feedback_update, inserted_id)
    except Exception as e:
        logger.error(f"Error while adding auto tags: {e}")


async def get_unique_tags():
    return await tags_collection.distinct('name')


async def get_user(username: str):
    user = await user_collection.find_one({"username": username})
    return user


async def get_image_ids_paginated(page_number, page_size):
    skip_count = (page_number - 1) * page_size
    cursor = images_collection.find({}, {'_id': 1}).skip(skip_count).limit(page_size)
    return [document['_id'] async for document in cursor]


async def get_image_document(inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        return await images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None

