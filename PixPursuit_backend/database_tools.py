from setup import connect_to_mongodb
from logging_config import setup_logging
import numpy as np
from sklearn.cluster import DBSCAN
from bson import ObjectId
from image_to_space import delete_image_from_space
from celery import shared_task
import asyncio

logger = setup_logging(__name__)
async_images_collection, sync_images_collection, async_tags_collection, sync_tags_collection, sync_faces_collection, async_faces_collection, user_collection, album_collection = connect_to_mongodb()


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
            {"$push": {"sons": str(new_album_id)}}
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


async def add_names(inserted_id, anonymous_index, new_name):
    try:
        if isinstance(inserted_id, str):
            inserted_id = ObjectId(inserted_id)

        image = await get_image_document(inserted_id)
        if not image:
            logger.error(f"Image not found with ID: {inserted_id}")
            return False

        if anonymous_index < 0 or anonymous_index >= len(image['user_faces']):
            logger.error(f"Invalid anonymous index: {anonymous_index}")
            return False

        old_name = image['user_faces'][anonymous_index]

        image['user_faces'][anonymous_index] = new_name

        await async_images_collection.update_one(
            {"_id": inserted_id},
            {"$set": {"user_faces": image['user_faces']}}
        )

        update_names_in_db.delay(old_name, new_name)

        logger.info(f"Successfully updated name for image: {inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error while adding name: {e}")
        return False


async def add_feedback(tag, is_positive, user, inserted_id):
    try:
        inserted_id_obj = ObjectId(inserted_id)
        image_document = await get_image_document(inserted_id)
        if not image_document:
            logger.error(f"No image found with ID: {inserted_id}")
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
            {'_id': inserted_id_obj},
            {'$set': {'feedback': feedback, 'feedback_history': feedback_history}}
        )

        logger.info(f"Feedback updated for image: {inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return False


def add_feedback_sync(auto_tags, inserted_id):
    try:
        inserted_id_obj = ObjectId(inserted_id)
        image_document = sync_images_collection.find_one({'_id': inserted_id_obj})
        existing_feedback = image_document.get('feedback', {})
        for tag in auto_tags:
            existing_feedback.setdefault(tag, {"positive": 0, "negative": 0})

        existing_feedback = {tag: data for tag, data in existing_feedback.items() if tag in auto_tags}

        sync_images_collection.update_one(
            {'_id': inserted_id_obj},
            {'$set': {'feedback': existing_feedback}}
        )

        logger.info("Successfully updated feedback for auto tags")
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


async def add_like(is_positive, username, inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
    except Exception as e:
        logger.error(f"Invalid inserted_id: {e}")
        return False

    try:
        update_result = await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$inc': {'likes': 1 if is_positive else -1}}
        )
        await async_images_collection.update_one(
            {'_id': inserted_id},
            {'$addToSet': {'liked_by': username}} if is_positive else {'$pull': {'liked_by': username}}
        )
        return update_result.matched_count > 0 and update_result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating likes: {e}")
        return False


async def add_view(inserted_id):
    try:
        inserted_id = ObjectId(inserted_id)
    except Exception as e:
        logger.error(f"Invalid inserted_id: {e}")
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


def add_auto_tags(inserted_id, predicted_tags):
    try:
        if not predicted_tags:
            return
        inserted_id_obj = ObjectId(inserted_id) if isinstance(inserted_id, str) else inserted_id

        image_document = sync_images_collection.find_one({'_id': inserted_id_obj})
        if not image_document:
            logger.error(f"No document found with id: {inserted_id}")
            return

        user_tags = image_document.get('user_tags', [])
        auto_tags_to_add = [tag for tag in predicted_tags if tag not in user_tags]

        if auto_tags_to_add:
            sync_images_collection.update_one(
                {'_id': inserted_id_obj},
                {'$set': {'auto_tags': auto_tags_to_add}}
            )

        if auto_tags_to_add:
            add_feedback_sync(auto_tags_to_add, inserted_id_obj)

        logger.info(f"Added auto tags: {auto_tags_to_add}")
    except Exception as e:
        logger.error(f"Error while adding auto tags: {e}")


async def add_photos_to_album(image_ids, album_id):
    try:
        album_id = ObjectId(album_id)
        if not isinstance(image_ids, list):
            image_ids = [image_ids]

        update_result = await album_collection.update_one(
            {"_id": album_id},
            {"$push": {"images": {"$each": image_ids}}}
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
            {'$pullAll': {'images': str(image_ids)}}
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
                {'_id': ObjectId(album['parent'])},
                {'$pull': {'sons': str(album_id)}}
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

            await album_collection.update_many({}, {"$pull": {"images": str(image_id)}})

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
                await async_tags_collection.update_one({"name": tag}, {"$set": {"name": "NULL"}})

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


def add_something_to_image(field_to_set, data, filename):
    sync_images_collection.update_one(
        {'filename': filename},
        {'$set': {field_to_set: data}}
    )


def insert_many_faces(faces_records):
    sync_faces_collection.insert_many(faces_records)


async def fetch_all_embeddings():
    try:
        cursor = async_faces_collection.find({})
        embeddings = []
        ids = []
        async for doc in cursor:
            embeddings.append(np.array(doc['face_emb']))
            ids.append(doc['_id'])
        return embeddings, ids
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return None


def cluster_embeddings(embeddings):
    try:
        embeddings_array = np.array(embeddings)
        dbscan = DBSCAN(eps=0.8, min_samples=3)
        clusters = dbscan.fit_predict(embeddings_array)
        return clusters
    except Exception as e:
        logger.exception(f"Clustering failed: {e}")
        raise


@shared_task(name='database_tools.group_faces')
def group_faces():
    async def async_task():
        cursor = async_images_collection.find({'embeddings': {'$exists': True, '$not': {'$size': 0}}})
        images = await cursor.to_list(length=None)

        all_embeddings = [emb for image in images for emb in image['embeddings']]

        if not all_embeddings:
            logger.info("No embeddings found for clustering.")
            return

        embeddings_array = np.array(all_embeddings)
        clustering = DBSCAN(eps=0.8, min_samples=3).fit(embeddings_array)

        label_idx = 0
        for image in images:
            num_embeddings = len(image['embeddings'])
            if num_embeddings > 0:
                image_clusters = clustering.labels_[label_idx:label_idx + num_embeddings]
                label_idx += num_embeddings

                current_document = await async_images_collection.find_one({'_id': image['_id']})
                current_user_faces = current_document.get('user_faces', [])

                updated_user_faces = []
                for idx, user_face in enumerate(current_user_faces):
                    if user_face.startswith('anon'):
                        updated_user_faces.append(
                            'anon' + str(image_clusters[idx] if idx < len(image_clusters) else ''))
                    else:
                        updated_user_faces.append(user_face)

                await async_images_collection.update_one(
                    {'_id': image['_id']},
                    {'$set': {
                        'auto_faces': image_clusters.tolist(),
                        'user_faces': updated_user_faces
                    }},
                    upsert=False
                )
        embeddings, ids = await fetch_all_embeddings()
        if embeddings:  # Proceed only if there are embeddings
            clusters = cluster_embeddings(embeddings)
            for idx, cluster_id in enumerate(clusters):
                group_id = f"face{cluster_id}"
                await async_faces_collection.update_one(
                    {'_id': ObjectId(ids[idx])},
                    {'$set': {'group': group_id}}
                )
            logger.info("Faces have been successfully grouped.")
        else:
            logger.info("No embeddings found to cluster.")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())


@shared_task(name='database_tools.update_names_in_db')
def update_names_in_db(old_name, new_name):
    async def async_task():
        try:
            if not all(isinstance(name, str) for name in [old_name, new_name]):
                logger.error("Names must be strings")
                return False

            update_result = await async_images_collection.update_many(
                {"user_faces": old_name},
                {"$set": {"user_faces.$": new_name}}
            )

            if update_result.modified_count > 0:
                logger.info(f"Successfully updated {update_result.modified_count} documents.")
                return True
            else:
                logger.info("No documents found with the old name.")
                return False
        except Exception as e:
            logger.error(f"Error while updating names: {e}")
            return False

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())