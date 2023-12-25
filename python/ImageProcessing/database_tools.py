from setup import connect_to_mongodb
from flask import current_app
import logging
from bson import ObjectId
from celery_config import celery
import torch
from tag_prediction_tools import load_model_state
import asyncio

logger = logging.getLogger(__name__)

database_client, images_collection, tags_collection = connect_to_mongodb()


async def save_to_database(data):
    try:
        face_embeddings, detected_objects, image_url, exif_data, features = data
        embeddings_list = [emb.tolist() for emb in face_embeddings] if face_embeddings is not None else []
        features_list = features.tolist() if features is not None else []

        image_record = {
            'image_url': image_url,
            'embeddings': embeddings_list,
            'detected_objects': detected_objects,
            'metadata': exif_data,
            'features': features_list,
            'user_tags': [],
            'auto_tags': [],
            'feedback': {},
            'description': ""
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
        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'feedback': feedback}}
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


async def get_unique_tags():
    return await tags_collection.distinct('name')


async def get_image_document(inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        return await images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


async def predictions_to_tag_names(predictions):
    all_tags = await tags_collection.find({}).to_list(None)
    index_to_tag = {i: tag['name'] for i, tag in enumerate(all_tags)}
    return [index_to_tag[idx] for idx in predictions if idx in index_to_tag]


@celery.task(name='database_tools.predict_and_update_tags')
def predict_and_update_tags(image_id, features):
    logger.info(f"Predicting and updating tags")

    async def async_task():
        with current_app.app_context():
            tag_predictor = load_model_state()
            features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
            predicted_indices = tag_predictor.predict_tags(features_tensor)
            predicted_tag_names = await predictions_to_tag_names(predicted_indices)
            await images_collection.update_one(
                {'_id': image_id},
                {'$set': {'auto_tags': predicted_tag_names}}
                )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())
