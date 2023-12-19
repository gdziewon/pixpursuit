from setup import connect_to_mongodb
from flask import current_app
import torch
from celery_config import celery
from bson import ObjectId


database_client, images_collection, tags_collection = connect_to_mongodb()


def save_to_database(face_embeddings, detected_objects, image_byte_arr, exif_data, features):
    try:
        embeddings_list = [emb.tolist() for emb in face_embeddings] if face_embeddings is not None else []
        features_list = features.tolist() if features is not None else []

        image_record = {
            'image_data': image_byte_arr,
            'embeddings': embeddings_list,
            'detected_objects': detected_objects,
            'metadata': exif_data,
            'features': features_list,
            'user_tags': [],
            'auto_tags': [],
            'feedback': {}
        }

        return images_collection.insert_one(image_record).inserted_id
    except Exception as e:
        print(f"Error saving to database: {e}")
        return None


def add_tags(tags, inserted_id):
    inserted_id = ObjectId(inserted_id)
    update_result = images_collection.update_one(
        {'_id': inserted_id},
        {'$addToSet': {'user_tags': {'$each': tags}}}
    )
    if update_result.matched_count == 0:
        return False

    for tag in tags:
        if not tags_collection.find_one({'name': tag}):
            tag_record = {'name': tag}
            tags_collection.insert_one(tag_record)

    return True


def add_feedback(feedback, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        image_document = images_collection.find_one({'_id': inserted_id})

        if image_document:
            images_collection.update_one({'_id': inserted_id}, {'$set': {'feedback': feedback}})
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating feedback: {e}")
        return False


def get_unique_tags():
    return tags_collection.distinct('name')


def get_image_document(inserted_id):
    inserted_id = ObjectId(inserted_id)
    image_document = images_collection.find_one({'_id': inserted_id})
    return image_document


def predictions_to_tag_names(predictions):
    all_tags = list(tags_collection.find({}))

    index_to_tag = {i: tag['name'] for i, tag in enumerate(all_tags)}

    predicted_tag_names = [index_to_tag[idx] for idx in predictions if idx in index_to_tag]

    return predicted_tag_names


@celery.task(name='database_tools.predict_and_update_tags')
def predict_and_update_tags(image_id, features):
    with current_app.app_context():
        from app import tag_predictor
        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)

        predicted_indices = tag_predictor.predict_tags(features_tensor)

        predicted_tag_names = predictions_to_tag_names(predicted_indices)

        images_collection.update_one(
            {'_id': image_id},
            {'$set': {'auto_tags': predicted_tag_names}}
        )
