from config.database_config import connect_to_mongodb
from config.logging_config import setup_logging
from bson import ObjectId
from databases.image_to_space import delete_image_from_space
from pymongo import UpdateOne
from tenacity import retry, stop_after_attempt, wait_fixed

logger = setup_logging(__name__)
async_images_collection, sync_images_collection, async_tags_collection, sync_tags_collection, sync_faces_collection, async_faces_collection, user_collection, album_collection = connect_to_mongodb()


def to_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception as e:
        logger.error(f"Invalid id: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def save_image_to_database(data, username, album_id):
    try:
        if not album_id:
            album_id = await get_root_id()

        image_url, thumbnail_url, filename, exif_data = data

        image_record = {
            'image_url': image_url,
            'thumbnail_url': thumbnail_url,
            'filename': filename,
            'embeddings': [],
            'embeddings_box': [],
            'detected_objects': {},
            'metadata': exif_data,
            'features': [],
            'user_tags': [],
            'auto_tags': [],
            'user_faces': [],
            'auto_faces': [],
            'backlog_faces': [],
            'unknown_faces': 0,
            'feedback': {},
            'feedback_history': {},
            'description': "",
            'likes': 0,
            'liked_by': [],
            'views': 0,
            'added_by': username,
            'album_id': str(album_id)
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def create_album(album_name, parent_id):
    if not parent_id:
        parent_id = await get_root_id()

    new_album = {
        "name": album_name,
        "parent": str(parent_id),
        "sons": [],
        "images": []
    }
    result = await album_collection.insert_one(new_album)
    new_album_id = result.inserted_id

    parent_id = to_object_id(parent_id)
    if parent_id is None:
        return None

    await album_collection.update_one(
        {"_id": parent_id},
        {"$push": {"sons": str(new_album_id)}}
    )

    return new_album_id


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_tags_to_images(tags, inserted_ids):
    for inserted_id in inserted_ids:
        inserted_id = to_object_id(inserted_id)
        if not inserted_id:
            continue

        if not tags:
            return False

        try:
            tags = [tag for tag in tags if tag != '']

            bulk_operations = [UpdateOne({'_id': inserted_id}, {'$addToSet': {'user_tags': tag}}) for tag in tags]
            await async_images_collection.bulk_write(bulk_operations)

            for tag in tags:
                if not await async_tags_collection.find_one({'name': tag}):
                    await async_tags_collection.insert_one({"name": tag, "count": 1})
                else:
                    await async_tags_collection.update_one({"name": tag}, {"$inc": {"count": 1}}, upsert=True)

        except Exception as e:
            logger.error(f"Error adding tags to image {inserted_id}: {e}")
            continue

    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_tags_to_albums(tags, album_ids):
    for album_id in album_ids:
        try:
            album = await get_album(album_id)
            if not album:
                continue

            image_ids = album.get('images', [])
            await add_tags_to_images(tags, image_ids)

            sub_album_ids = album.get('sons', [])
            if sub_album_ids:
                await add_tags_to_albums(sub_album_ids, tags)

        except Exception as e:
            logger.error(f"Error while adding tags to albums: {e}")
            continue

    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_feedback(tag, is_positive, user, inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        image_document = await get_image_document(inserted_id)
        if not image_document:
            logger.error(f"No image found with ID: {str(inserted_id)}")
            return False

        feedback = image_document.get('feedback', {})
        feedback_history = image_document.get('feedback_history', {})
        user_feedback_history = feedback_history.get(user, {})
        previous_feedback = user_feedback_history.get(tag)

        if previous_feedback is not None:
            if previous_feedback != is_positive:
                feedback[tag]['positive'] += 1 if is_positive else -1
                feedback[tag]['negative'] += -1 if is_positive else 1
        else:
            feedback[tag] = feedback.get(tag, {'positive': 0, 'negative': 0})
            feedback[tag]['positive'] += 1 if is_positive else 0
            feedback[tag]['negative'] += 0 if is_positive else 1

        user_feedback_history[tag] = is_positive
        feedback_history[user] = user_feedback_history

        await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'feedback': feedback, 'feedback_history': feedback_history}}
        )

        logger.info(f"Feedback updated for image: {str(inserted_id)}")
        return True
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_feedback_sync(auto_tags, inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        image_document = sync_images_collection.find_one({'_id': inserted_id})
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_description(description, inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_like(is_positive, username, inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        update_result = await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$inc': {'likes': 1 if is_positive else -1}}
        )
        if is_positive:
            await user_collection.update_one(
                {'username': username},
                {'$addToSet': {'liked': str(inserted_id)}}
            )
            await async_images_collection.update_one(
                {'_id': inserted_id},
                {'$addToSet': {'liked_by': username}}
            )
        else:
            await user_collection.update_one(
                {'username': username},
                {'$pull': {'liked': str(inserted_id)}}
            )
            await async_images_collection.update_one(
                {'_id': inserted_id},
                {'$pull': {'liked_by': username}}
            )
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating likes: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_view(inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        update_result = await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$inc': {'views': 1}}
        )
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating views: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_auto_tags(inserted_id, predicted_tags):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return

    try:
        image_document = sync_images_collection.find_one({'_id': inserted_id})
        if not image_document:
            logger.error(f"No document found with id: {str(inserted_id)}")
            return

        user_tags = image_document.get('user_tags', [])
        auto_tags_to_add = [tag for tag in predicted_tags if tag not in user_tags]

        if auto_tags_to_add:
            sync_images_collection.update_one(
                {'_id': inserted_id},
                {'$set': {'auto_tags': auto_tags_to_add}}
            )

        if auto_tags_to_add:
            add_feedback_sync(auto_tags_to_add, inserted_id)

    except Exception as e:
        logger.error(f"Error while adding auto tags: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_photos_to_album(image_ids, album_id):
    album_id = to_object_id(album_id)
    if not album_id:
        return False

    if not isinstance(image_ids, list):
        image_ids = [image_ids]

    try:
        update_result = await album_collection.update_one(
            {"_id": album_id},
            {"$push": {"images": {"$each": image_ids}}}
        )
        return update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error adding photos to album: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def relocate_to_album(prev_album_id, new_album_id=None, image_ids=None):
    prev_album_id = to_object_id(prev_album_id)
    new_album_id = to_object_id(new_album_id) if new_album_id else await get_root_id()

    if not image_ids:
        cursor = async_images_collection.find({'album_id': prev_album_id}, {'_id': 1})
        image_ids = [image['_id'] for image in await cursor.to_list(length=100)]

    bulk_operations = [UpdateOne({'_id': image_id}, {'$set': {'album_id': new_album_id}}) for image_id in image_ids]

    if bulk_operations:
        await async_images_collection.bulk_write(bulk_operations)

    await add_photos_to_album(image_ids, new_album_id)

    await album_collection.update_one(
        {'_id': prev_album_id},
        {'$pullAll': {'images': [str(image_id) for image_id in image_ids]}}
    )
    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def delete_albums(album_ids, is_top_level=True):
    for album_id in album_ids:
        try:
            album_id = to_object_id(album_id)
            album = await get_album(album_id)
            if not album:
                return False

            image_ids = [to_object_id(image_id) for image_id in album['images']]
            await delete_images(image_ids)

            sub_album_ids = [to_object_id(sub_album_id) for sub_album_id in album['sons']]
            await delete_albums(sub_album_ids, is_top_level=False)

            if is_top_level and album['parent']:
                parent_id = to_object_id(album['parent'])
                await album_collection.update_one(
                    {'_id': parent_id},
                    {'$pull': {'sons': str(album_id)}}
                )

            await album_collection.delete_one({'_id': album_id})
            logger.info(f"Successfully deleted album: {str(album_id)}")
        except Exception as e:
            logger.error(f"Error deleting album {album_id}: {e}")
            return False

    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def delete_images(image_ids):
    for image_id in image_ids:
        try:
            image_id = to_object_id(image_id)
            image = await get_image_document(image_id)
            if not image:
                return False

            await user_collection.update_many(
                {},
                {'$pull': {'liked': str(image_id)}}
            )

            await album_collection.update_many({}, {"$pull": {"images": str(image_id)}})

            await decrement_tags_count(image['user_tags'])

            await delete_image_from_space(image['image_url'])

            await delete_image_from_space(image['thumbnail_url'])

            await async_images_collection.delete_one({"_id": image_id})
            logger.info(f"Successfully deleted image: {str(image_id)}")
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {e}")
            return False

    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def remove_tags_from_image(image_id, tags_to_remove):
    image_id = to_object_id(image_id)
    if not image_id:
        return False

    try:
        image = await get_image_document(image_id)
        if not image:
            return False

        await async_images_collection.update_one(
            {"_id": image_id},
            {"$pull": {"user_tags": {"$in": tags_to_remove}}}
        )
        await decrement_tags_count(tags_to_remove)
        return True
    except Exception as e:
        logger.error(f"Error while removing tags: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def decrement_tags_count(tags):
    try:
        for tag in tags:
            await async_tags_collection.update_one(
                {"name": tag},
                {"$inc": {"count": -1}}
            )
            tag_doc = await async_tags_collection.find_one({"name": tag})
            if tag_doc and tag_doc['count'] <= 0:
                await async_tags_collection.update_one({"name": tag}, {"$set": {"name": "NULL"}})

        from tag_prediction.tag_prediction_tools import update_model_tags
        await update_model_tags()
    except Exception as e:
        logger.error(f"Error while decrementing tags count: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_unique_tags():
    return sync_tags_collection.distinct('name')


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_user(username: str):
    user = await user_collection.find_one({"username": username})
    return user


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_image_ids_paginated(page_number, page_size):
    skip_count = (page_number - 1) * page_size
    cursor = sync_images_collection.find({}, {'_id': 1}).skip(skip_count).limit(page_size)
    return [str(document['_id']) for document in cursor]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_image_document(inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return None

    try:
        return await async_images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_image_document_sync(inserted_id):
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return None

    try:
        return sync_images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_album(album_id):
    album_id = to_object_id(album_id)
    if not album_id:
        return None

    try:
        return await album_collection.find_one({'_id': album_id})
    except Exception as e:
        logger.error(f"Error retrieving album: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def add_something_to_image(field_to_set, data, filename):
    sync_images_collection.update_one(
        {'filename': filename},
        {'$set': {field_to_set: data}}
    )


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def rename_album(name, album_id):
    album_id = to_object_id(album_id)
    if not album_id:
        return False

    try:
        update_result = await album_collection.update_one(
            {'_id': album_id},
            {'$set': {'name': name}}
        )
        if update_result.matched_count > 0 and update_result.modified_count > 0:
            logger.info(f"Successfully renamed album: {str(album_id)} to {name}")
            return True
        else:
            logger.error(f"Failed to rename album: {str(album_id)}")
            return False
    except Exception as e:
        logger.error(f"Error renaming album: {e}")
        return False
