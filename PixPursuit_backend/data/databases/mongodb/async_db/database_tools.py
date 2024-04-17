from bson import ObjectId
from config.database_config import connect_to_mongodb
from config.logging_config import setup_logging
from data.databases.space_manager import SpaceManager
from pymongo import UpdateOne
from tenacity import retry, stop_after_attempt, wait_fixed
from utils.function_utils import to_object_id
from data.databases.mongodb.sync_db.face_operations import update_names
from data.databases.mongodb.sync_db.face_operations import delete_faces_associated_with_images

logger = setup_logging(__name__)

images_collection, tags_collection, faces_collection, user_collection, album_collection = connect_to_mongodb()
SpaceManager = SpaceManager()


async def get_image_record(data: tuple[str, str, str, dict],
                           username: str, album_id: ObjectId or str) -> dict or None:
    """
    Get the image record to be saved in the database.

    :param data: A tuple containing the image URL, thumbnail URL, filename, and EXIF data.
    :param username: The username of the user adding the image.
    :param album_id: The ID of the album to which the image belongs.
    :return: A dictionary containing the image record.
    """
    try:
        image_url, thumbnail_url, filename, exif_data = data

        album_name = (await get_album(album_id))['name']

        image_record = {
            'image_url': image_url,
            'thumbnail_url': thumbnail_url,
            'filename': filename,
            'embeddings': [],
            'embeddings_box': [],
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
    """
    Save image data to the database.

    :param data: A tuple containing the image URL, thumbnail URL, filename, and EXIF data.
    :param username: The username of the user adding the image.
    :param album_id: The ID of the album to which the image belongs.
    :return: The ID of the inserted image record.
    """
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
    """
    Create a new album in the database.

    :param album_name: The name of the new album.
    :param parent_id: The ID of the parent album.
    :return: The ID of the inserted album.
    """
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
    """
    Add tags to images in the database.
    :param tags: A list of tags to add.
    :param inserted_ids: A list of image IDs to which to add the tags.
    :return: True if the tags were added successfully, False otherwise.
    """
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
    """
    Add tags to albums in the database.

    :param tags: A list of tags to add.
    :param album_ids: A list of album IDs to which to add the tags.
    :return: True if the tags were added successfully, False otherwise.
    """
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
    """
    Add feedback to an image in the database.
    :param tag: The tag for which to add feedback.
    :param is_positive: Whether the feedback is positive or negative.
    :param user: The username of the user providing feedback.
    :param inserted_id: The ID of the image to which to add feedback.
    :return: True if the feedback was added successfully, False otherwise.
    """
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
    """
    Add a description to an image in the database.

    :param description: The description to add.
    :param inserted_id: The ID of the image to which to add the description.
    :return: True if the description was added successfully, False otherwise.
    """
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
    """
    Add a like to an image in the database.

    :param is_positive: Whether the like is positive or negative.
    :param username: The username of the user adding the like.
    :param inserted_id: The ID of the image to which to add the like.
    :return: True if the like was added successfully, False otherwise.
    """
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
    """
    Add a view to an image in the database.

    :param inserted_id: The ID of the image to which to add the view.
    :return: True if the view was added successfully, False otherwise.
    """
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
    """
    Add photos to an album in the database.

    :param image_ids: The ID of the image or a list of image IDs to add to the album.
    :param album_id: The ID of the album to which to add the photos.
    :return: True if the photos were added successfully, False otherwise.
    """
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
    """
    Relocate images from one album to another.

    :param prev_album_id: The ID of the previous album.
    :param new_album_id: The ID of the new album.
    :param image_ids: A list of image IDs to relocate.
    :return: True if the images were relocated successfully, False otherwise.
    """
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
    """
    Delete albums from the database.

    :param album_ids: A list of album IDs to delete.
    :param is_top_level: Whether the album is root of the local tree.
    :return: True if the albums were deleted successfully, False otherwise.
    """
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
    """
    Delete images from the database.

    :param image_ids: A list of image IDs to delete.
    :return: True if the images were deleted successfully, False otherwise.
    """
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
    """
    Remove tags from an image in the database.
    :param image_id: The ID of the image from which to remove tags.
    :param tags_to_remove: A list of tags to remove.
    :return: True if the tags were removed successfully, False otherwise.
    """
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
    """
    Increment the count of unique tags in the database.

    :param tags: A list of tags to increment.
    :return: True if the tags were incremented successfully, False otherwise.
    """
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
    """
    Decrement the count of unique tags in the database.

    :param tags: A list of tags to decrement.
    :return: True if the tags were decremented successfully, False otherwise.
    """
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
    """
    Get the ID of the root album.

    :return: The ID of the root album.
    """
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
    """
    Get a user document by username from the database.
    :param username: The username of the user to retrieve.
    :return: The user document if found, None otherwise.
    """
    user = await user_collection.find_one({"username": username})
    return user


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def create_user(email: str, password: str) -> dict or None:
    """
    Create a new user in the database.

    :param email: The email address of the new user.
    :param password: Hashed password of the new user.
    :return: Inserted user document if successful, None otherwise.
    """
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
    """
    Mark a user's email as verified in the database.

    :param user_id: The ID of the user to mark as verified.
    :return: True if the email was marked as verified successfully, False otherwise.
    """
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
    """
    Get an image document by ID from the database.

    :param inserted_id: The ID of the image to retrieve.
    :return: The image document if found, None otherwise.
    """
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
    """
    Get an album by ID from the database.

    :param album_id: The ID of the album to retrieve.
    :return: The album document if found, None otherwise.
    """
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
    """
    Rename an album in the database.

    :param name: The new name for the album.
    :param album_id: The ID of the album to rename.
    :return: True if the album was renamed successfully, False otherwise.
    """
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
    """
    Add a name to an anonymous face in an image.

    :param inserted_id: The ID of the image to which to add the name.
    :param anonymous_index: The index of the anonymous face.
    :param new_name: The name to add.
    :return: True if the name was added successfully, False otherwise.
    """
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
