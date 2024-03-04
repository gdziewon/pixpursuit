from bson import ObjectId
from config.database_config import connect_to_mongodb_async
from config.logging_config import setup_logging
from databases.space_manager import SpaceManager
from pymongo import UpdateOne
from tenacity import retry, stop_after_attempt, wait_fixed
from utils.function_utils import to_object_id
from databases.face_operations import update_names
from databases.face_operations import delete_faces_associated_with_images

logger = setup_logging(__name__)

images_collection, tags_collection, faces_collection, user_collection, album_collection = connect_to_mongodb_async()
SpaceManager = SpaceManager()


async def get_image_record(data: tuple[str, str, str, dict],
                           username: str, album_id: ObjectId or str) -> dict or None:
    try:
        image_url, thumbnail_url, filename, exif_data = data

        album_name = (await get_album(album_id))['name']

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
            'album_id': str(album_id),
            'album_name': album_name
        }
        return image_record
    except Exception as e:
        logger.error(f"Error getting image record: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def save_image_to_database(data: tuple[str, str, str, dict], username: str, album_id: ObjectId or str) -> str or None:
    try:
        if not album_id or album_id == "root":
            album_id = await get_root_id()
        else:
            album_id = to_object_id(album_id)
            if not album_id:
                return None

        image_record = await get_image_record(data, username, album_id)
        if not image_record:
            return None

        result = await images_collection.insert_one(image_record)
        inserted_id = str(result.inserted_id)

        await add_photos_to_album(inserted_id, album_id)

        logger.info(f"Successfully saved data for image: {inserted_id}")
        return inserted_id
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def create_album(album_name: str, parent_id: ObjectId or str = None) -> ObjectId or None:
    if not parent_id:
        parent_id = await get_root_id()
    parent_id = to_object_id(parent_id)

    if not parent_id:
        return None

    new_album = {
        "name": album_name,
        "parent": str(parent_id),
        "sons": [],
        "images": []
    }
    result = await album_collection.insert_one(new_album)
    new_album_id = result.inserted_id

    await album_collection.update_one(
        {"_id": parent_id},
        {"$push": {"sons": str(new_album_id)}}
    )

    return new_album_id


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_tags_to_images(tags: list[str], inserted_ids: list[str]) -> bool:
    for inserted_id in inserted_ids:
        inserted_id = to_object_id(inserted_id)
        if not inserted_id:
            continue

        if not tags:
            return False

        try:
            tags = [tag for tag in tags if tag != '']

            bulk_operations = [UpdateOne({'_id': inserted_id}, {'$addToSet': {'user_tags': tag}}) for tag in tags]
            await images_collection.bulk_write(bulk_operations)

            await increment_tags_count(tags)

        except Exception as e:
            logger.error(f"Error adding tags to image {inserted_id}: {e}")
            continue

    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_tags_to_albums(tags: list[str], album_ids: list[str]) -> bool:
    for album_id in album_ids:
        try:
            album = await get_album(album_id)
            if not album:
                continue

            image_ids = album.get('images', [])
            await add_tags_to_images(tags, image_ids)

            sub_album_ids = album.get('sons', [])
            if sub_album_ids:
                await add_tags_to_albums(tags, sub_album_ids)

        except Exception as e:
            logger.error(f"Error while adding tags to albums: {e}")
            continue

    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_feedback(tag: str, is_positive: bool, user: str, inserted_id: ObjectId or str) -> bool:
    try:
        inserted_id = to_object_id(inserted_id)
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

        await images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'feedback': feedback, 'feedback_history': feedback_history}}
        )

        logger.info(f"Feedback updated for image: {str(inserted_id)}")
        return True
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_description(description: str, inserted_id: ObjectId or str) -> bool:
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            {'$set': {'description': description}}
        )
        logger.info("Successfully added description")
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating description: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_like(is_positive: bool, username: str, inserted_id: ObjectId or str) -> bool:
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            {'$inc': {'likes': 1 if is_positive else -1}}
        )

        image_document = await images_collection.find_one({'_id': inserted_id})
        if image_document['likes'] < 0:
            await images_collection.update_one(
                {'_id': inserted_id},
                {'$set': {'likes': 0}}
            )

        operation = '$addToSet' if is_positive else '$pull'
        await user_collection.update_one(
            {'username': username},
            {operation: {'liked': str(inserted_id)}}
        )
        await images_collection.update_one(
            {'_id': inserted_id},
            {operation: {'liked_by': username}}
        )

        logger.info(f"Successfully added like to image: {str(inserted_id)}")
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating likes: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_view(inserted_id: ObjectId or str) -> bool:
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return False

    try:
        update_result = await images_collection.update_one(
            {'_id': inserted_id},
            {'$inc': {'views': 1}}
        )
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating views: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_photos_to_album(image_ids: ObjectId or str, album_id: ObjectId or str) -> bool:
    album_id = to_object_id(album_id)
    if not album_id:
        logger.error(f"Invalid album_id provided: {album_id}")
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
async def relocate_to_album(prev_album_id: ObjectId or str, new_album_id: ObjectId or str,
                            image_ids: list[str]) -> bool:
    try:
        prev_album_id = to_object_id(prev_album_id)
        new_album_id = to_object_id(new_album_id) if new_album_id else await get_root_id()

        if not image_ids:
            cursor = images_collection.find({'album_id': prev_album_id}, {'_id': 1})
            image_ids = [image['_id'] for image in await cursor.to_list(length=100)]

        bulk_operations = [UpdateOne({'_id': image_id}, {'$set': {'album_id': new_album_id}}) for image_id in image_ids]

        if bulk_operations:
            await images_collection.bulk_write(bulk_operations)

        await add_photos_to_album(image_ids, new_album_id)

        update_result = await album_collection.update_one(
            {'_id': prev_album_id},
            {'$pullAll': {'images': [str(image_id) for image_id in image_ids]}}
        )
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error relocating images: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def delete_albums(album_ids: list[str], is_top_level: bool = True) -> bool:
    all_deleted_successfully = True
    for album_id in album_ids:
        try:
            album_id = to_object_id(album_id)
            album = await get_album(album_id)
            if not album:
                logger.error(f"No album found with ID: {album_id}")
                all_deleted_successfully = False
                continue

            image_ids = album['images']
            for image_id in image_ids:
                delete_image_result = await delete_images([image_id])
                if not delete_image_result:
                    logger.error(f"Error deleting image {image_id} in album {album_id}")
                    all_deleted_successfully = False
                    continue

            sub_album_ids = album['sons']
            sub_delete_success = await delete_albums(sub_album_ids, is_top_level=False)
            all_deleted_successfully = all_deleted_successfully and sub_delete_success

            if is_top_level and album['parent']:
                parent_id = to_object_id(album['parent'])
                await album_collection.update_one(
                    {'_id': parent_id},
                    {'$pull': {'sons': str(album_id)}}
                )

            await album_collection.delete_one({'_id': album_id})
            logger.info(f"Successfully deleted album: {album_id}")
        except Exception as e:
            logger.error(f"Error deleting album {album_id}: {e}")
            all_deleted_successfully = False

    return all_deleted_successfully


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def delete_images(image_ids: list[str]) -> bool:
    all_deleted_successfully = True
    for image_id in image_ids:
        try:
            image_id = to_object_id(image_id)
            image_document = await get_image_document(image_id)
            if not image_document:
                logger.error(f"No image found with ID: {str(image_id)}")
                all_deleted_successfully = False
                continue

            delete_faces_associated_with_images.delay([str(image_id)])

            await user_collection.update_many(
                {},
                {'$pull': {'liked': str(image_id)}}
            )

            await album_collection.update_many({}, {"$pull": {"images": str(image_id)}})

            await decrement_tags_count(image_document['user_tags'])

            await SpaceManager.delete_image_from_space(image_document['image_url'])
            await SpaceManager.delete_image_from_space(image_document['thumbnail_url'])
            await images_collection.delete_one({"_id": image_id})

            logger.info(f"Successfully deleted image: {str(image_id)}")
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {e}")
            all_deleted_successfully = False

    return all_deleted_successfully


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def remove_tags_from_image(image_id: ObjectId or str, tags_to_remove: list[str]) -> bool:
    try:
        image_id = to_object_id(image_id)
        image = await get_image_document(image_id)
        if not image:
            logger.error(f"No image found with ID: {str(image_id)}")
            return False

        await images_collection.update_one(
            {"_id": image_id},
            {"$pull": {"user_tags": {"$in": tags_to_remove}}}
        )
        await decrement_tags_count(tags_to_remove)
        return True
    except Exception as e:
        logger.error(f"Error while removing tags: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def increment_tags_count(tags: list[str]) -> bool:
    try:
        for tag in tags:
            if not await tags_collection.find_one({'name': tag}):
                await tags_collection.insert_one({"name": tag, "count": 1})
            else:
                await tags_collection.update_one({"name": tag}, {"$inc": {"count": 1}}, upsert=True)

        return True
    except Exception as e:
        logger.error(f"Error while incrementing tags count: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def decrement_tags_count(tags: list[str]) -> bool:
    try:
        for tag in tags:
            await tags_collection.update_one(
                {"name": tag},
                {"$inc": {"count": -1}}
            )
            tag_doc = await tags_collection.find_one({"name": tag})
            if tag_doc and tag_doc['count'] <= 0:
                await tags_collection.update_one({"name": tag}, {"$set": {"name": "NULL"}})

    except Exception as e:
        logger.error(f"Error while decrementing tags count: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_root_id() -> ObjectId or None:
    try:
        root_album = await album_collection.find_one({"name": "root", "parent": None})
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
async def get_user(username: str) -> dict or None:
    user = await user_collection.find_one({"username": username})
    return user


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def create_user(email: str, password: str) -> dict or None:
    email = email.lower()
    username = email.split('@')[0]
    user = await get_user(username)
    if user:
        return None
    try:
        user = {
            "username": username,
            "password": password,
            "email": email,
            "verified": False,
            "liked": []
        }
        result = await user_collection.insert_one(user)
        return result
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def mark_email_as_verified(user_id: ObjectId or str) -> bool:
    try:
        user_id = to_object_id(user_id)
        if not user_id:
            return False

        result = await user_collection.find_one_and_update(
            {"_id": user_id},
            {"$set": {"verified": True}}
        )
        logger.info(f"Successfully marked email as verified for user: {result['username']}")
        return True if result else False
    except Exception as e:
        logger.error(f"Error marking email as verified for user {user_id}: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_image_document(inserted_id: ObjectId or str) -> dict or None:
    inserted_id = to_object_id(inserted_id)
    if not inserted_id:
        return None

    try:
        return await images_collection.find_one({'_id': inserted_id})
    except Exception as e:
        logger.error(f"Error retrieving image document: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_album(album_id: ObjectId or str) -> dict or None:
    album_id = to_object_id(album_id)
    if not album_id:
        return None

    try:
        return await album_collection.find_one({'_id': album_id})
    except Exception as e:
        logger.error(f"Error retrieving album: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def rename_album(name: str, album_id: ObjectId or str) -> bool:
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def add_names(inserted_id: ObjectId or str, anonymous_index: int, new_name: str) -> bool:
    try:
        inserted_id = to_object_id(inserted_id)
        if not inserted_id:
            return False

        image = await get_image_document(inserted_id)
        if not image:
            logger.error(f"Image not found with ID: {inserted_id}")
            return False

        if anonymous_index < 0 or anonymous_index >= len(image['user_faces']):
            logger.error(f"Invalid anonymous index: {anonymous_index}")
            return False

        old_name = image['user_faces'][anonymous_index]

        image['user_faces'][anonymous_index] = new_name
        if old_name == "anon-1":
            await images_collection.update_one(
                {"_id": inserted_id},
                {"$set": {"user_faces": image['user_faces']},
                 "$inc": {"unknown_faces": 1}
                 }
            )
        else:
            image['backlog_faces'][anonymous_index] = new_name
            await images_collection.update_one(
                {"_id": inserted_id},
                {"$set": {
                    "user_faces": image['user_faces'],
                    "backlog_faces": image['backlog_faces']
                }}
            )
            update_names.delay(old_name, new_name)

        logger.info(f"Successfully updated name for image: {inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error while adding name: {e}")
        return False
