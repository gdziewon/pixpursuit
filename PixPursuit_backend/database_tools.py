from setup import connect_to_mongodb
from logging_config import setup_logging
from bson import ObjectId
from image_to_space import delete_image_from_space

logger = setup_logging(__name__)

async_images_collection, sync_images_collection, async_tags_collection, sync_tags_collection, user_collection, album_collection = connect_to_mongodb()


async def save_image_to_database(data, username, album_id):
    try:
        if not album_id:
            album_id = await get_root_id()

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
            'added_by': username,
            'album_id': album_id
        }
        result = await async_images_collection.insert_one(image_record)
        inserted_id = str(result.inserted_id)
        logger.info(f"Inserted_id in save_to_database: {str(inserted_id)}")
        await add_photos_to_album(inserted_id, album_id)

        logger.info(f"Successfully saved data for image: {image_url}")
        return inserted_id
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return None


async def create_album(album_name, parent_id):
    if not parent_id:
        parent_id = await get_root_id()

    new_album = {
        "name": album_name,
        "parent": parent_id,
        "sons": [],
        "images": []
    }
    result = await album_collection.insert_one(new_album)
    new_album_id = result.inserted_id

    try:
        parent_id = ObjectId(parent_id)
    except Exception as e:
        logger.error(f"Invalid parent_id: {e}")
        return None

    if parent_id is not None:
        await album_collection.update_one(
            {"_id": parent_id},
            {"$push": {"sons": new_album_id}}
        )

    return new_album_id


async def add_tags(tags, inserted_id):

    try:
        inserted_id = ObjectId(inserted_id)
    except Exception as e:
        logger.error(f"Invalid inserted_id: {e}")
        return False

    try:
        update_result = await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$addToSet': {'user_tags': {'$each': tags}}}
        )
        if update_result.matched_count == 0:
            return False

        for tag in tags:
            if not await async_tags_collection.find_one({'name': tag}):
                await async_tags_collection.insert_one({"name": tag, "count": 1})
            else:
                await async_tags_collection.update_one({"name": tag}, {"$inc": {"count": 1}}, upsert=True)

        return True
    except Exception as e:
        logger.error(f"Error adding tags: {e}")
        return False


async def add_feedback(feedback, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
    except Exception as e:
        logger.error(f"Invalid inserted_id: {e}")
        return False

    try:
        update_operations = {'$set': {f'feedback.{tag}': value for tag, value in feedback.items() if value is not False},
                             '$setOnInsert': {f'feedback.{tag}': False for tag, value in feedback.items() if value is False}}

        await async_images_collection.update_one(
            {'_id': inserted_id},
            update_operations,
            upsert=True
        )

        logger.info(f"Successfully added feedback")
        return True
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False


def add_feedback_sync(feedback, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
    except Exception as e:
        logger.error(f"Invalid inserted_id: {e}")
        return False

    try:
        update_operations = {'$set': {f'feedback.{tag}': value for tag, value in feedback.items() if value is not False},
                             '$setOnInsert': {f'feedback.{tag}': False for tag, value in feedback.items() if value is False}}

        sync_images_collection.update_one(
            {'_id': inserted_id},
            update_operations,
            upsert=True
        )

        logger.info(f"Successfully added feedback")
        return True
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False


async def add_description(description, inserted_id):

    try:
        inserted_id = ObjectId(inserted_id)
    except Exception as e:
        logger.error(f"Invalid inserted_id: {e}")
        return False

    try:
        update_result = await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'description': description}}
        )
        logger.info("Successfully added description")
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating description: {e}")
        return False


def add_auto_tags(inserted_id, predicted_tags):
    try:
        if not predicted_tags:
            return
        inserted_id_obj = ObjectId(inserted_id) if isinstance(inserted_id, str) else inserted_id

        image_document = sync_images_collection.find_one({'_id': inserted_id_obj})
        user_tags = image_document.get('user_tags', [])
        feedback = image_document.get('feedback', {})
        filtered_predicted_tags = [tag for tag in predicted_tags if tag not in user_tags]

        sync_images_collection.update_one(
            {'_id': inserted_id_obj},
            {'$set': {'auto_tags': predicted_tags}}
        )

        feedback_update = {tag: feedback.get(tag, False) for tag in filtered_predicted_tags}
        logger.info(f"Added auto tags: {predicted_tags}")

        add_feedback_sync(feedback_update, inserted_id_obj)

    except Exception as e:
        logger.error(f"Error while adding auto tags: {e}")


async def add_photos_to_album(photo_ids, album_id):
    try:
        album_id = ObjectId(album_id)
        if not isinstance(photo_ids, list):
            photo_ids = [photo_ids]
        update_result = await album_collection.update_one(
            {"_id": album_id},
            {"$push": {"images": {"$each": photo_ids}}}
        )
        return update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error adding photos to album: {e}")
        return False


async def relocate_to_album(prev_album_id, new_album_id=None, image_ids=None):
    try:
        if not new_album_id:
            new_album_id = await get_root_id()
        else:
            new_album_id = ObjectId(new_album_id)

        if not image_ids:
            cursor = async_images_collection.find({'album_id': prev_album_id}, {'_id': 1})
            image_ids = []
            async for image in cursor:
                image_ids.append(image['_id'])

        for image_id in image_ids:
            await async_images_collection.update_one(
                {'_id': image_id},
                {'$set': {'album_id': new_album_id}}
            )

        await add_photos_to_album(image_ids, new_album_id)

        await album_collection.update_one(
            {'_id': prev_album_id},
            {'$pullAll': {'images': image_ids}}
        )
        return True

    except Exception as e:
        logger.error(f"Error relocating images: {e}")
        return False


async def delete_album(album_id):
    try:
        album = await get_album(album_id)
        if not album:
            return False

        album_id = ObjectId(album_id)
        await relocate_to_album(prev_album_id=album_id)

        if album['parent']:
            await album_collection.update_one(
                {'_id': album['parent']},
                {'$pull': {'sons': album_id}}
            )

        await album_collection.delete_one({'_id': album_id})
        return True
    except Exception as e:
        logger.error(f"Error deleting album: {e}")
        return False


async def delete_images(image_ids):
    for image_id in image_ids:
        image = await get_image_document(image_id)
        if not image:
            logger.warning(f"Could not find image {image_id}")
            return False

        try:
            image_id = ObjectId(image_id)
            await async_images_collection.delete_one({"_id": image_id})

            await album_collection.update_many({}, {"$pull": {"images": image_id}})

            await decrement_tags_count(image['user_tags'])

            logger.info(f"Removing image: {image['image_url']}")
            await delete_image_from_space(image['image_url'])

            logger.info(f"Removing thumbnail: {image['thumbnail_url']}")
            await delete_image_from_space(image['thumbnail_url'])

        except Exception as e:
            logger.error(f"Error while deleting image {image_id}: {e}")
            return False
    return True


async def remove_tags_from_image(image_id, tags_to_remove):
    try:
        image = await get_image_document(image_id)
        if not image:
            return False

        image_id = ObjectId(image_id)
        await async_images_collection.update_one(
            {"_id": image_id},
            {"$pull": {"user_tags": {"$in": tags_to_remove}}}
        )
        await decrement_tags_count(tags_to_remove)
        return True
    except Exception as e:
        logger.error(f"Error while removing tags: {e}")
        return False


async def decrement_tags_count(tags):
    try:
        for tag in tags:
            await async_tags_collection.update_one(
                {"name": tag},
                {"$inc": {"count": -1}}
            )
            tag_doc = await async_tags_collection.find_one({"name": tag})
            if tag_doc and tag_doc['count'] <= 0:
                await async_tags_collection.delete_one({"name": tag})

        from tag_prediction_tools import update_model_tags
        await update_model_tags()
    except Exception as e:
        logger.error(f"Error while decrementing tags count: {e}")
        return False


async def get_root_id():
    try:
        root_album = await album_collection.find_one({"name": "root"})
        if not root_album:
            root_album = {
                "name": "root",
                "parent": None,
                "sons": [],
                "images": []
            }
            result = (await album_collection.insert_one(root_album))
            root_album_id = result.inserted_id
        else:
            root_album_id = root_album['_id']

        return root_album_id
    except Exception as e:
        logger.error(f"Error retrieving root album: {e}")
        return None


def get_unique_tags():
    return sync_tags_collection.distinct('name')


async def get_user(username: str):
    user = await user_collection.find_one({"username": username})
    return user


def get_image_ids_paginated(page_number, page_size):
    skip_count = (page_number - 1) * page_size
    cursor = sync_images_collection.find({}, {'_id': 1}).skip(skip_count).limit(page_size)
    return [str(document['_id']) for document in cursor]


async def get_image_document(inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        return await async_images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


def get_image_document_sync(inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
        return sync_images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


async def get_album(album_id):
    try:
        album_id = ObjectId(album_id)
        return await album_collection.find_one({'_id': album_id})
    except Exception as e:
        logger.error(f"Error retrieving album: {e}")
        return None
