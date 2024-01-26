from config.database_config import connect_to_mongodb
from config.logging_config import setup_logging
from bson import ObjectId
from celery import shared_task
import asyncio
import numpy as np
from sklearn.cluster import DBSCAN
from databases.database_tools import get_image_document

logger = setup_logging(__name__)
async_images_collection, _, _, _, sync_faces_collection, async_faces_collection, _, _ = connect_to_mongodb()


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
        logger.error(f"Clustering failed: {e}")
        return []


def insert_many_faces(faces_records):
    sync_faces_collection.insert_many(faces_records)


@shared_task(name='face_operations.group_faces')
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


@shared_task(name='face_operations.update_names_in_db')
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
