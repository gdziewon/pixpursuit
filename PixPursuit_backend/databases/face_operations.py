from config.database_config import connect_to_mongodb_async, connect_to_mongodb_sync
from config.logging_config import setup_logging
from celery import shared_task
import asyncio
import numpy as np
from sklearn.cluster import DBSCAN
from tenacity import retry, stop_after_attempt, wait_fixed
from utils.function_utils import to_object_id

logger = setup_logging(__name__)
async_images_collection, _, _, _, _ = connect_to_mongodb_async()
sync_images_collection, _, sync_faces_collection, _, _ = connect_to_mongodb_sync()


def cluster_embeddings(embeddings):
    try:
        embeddings_array = np.array(embeddings)
        dbscan = DBSCAN(eps=0.8, min_samples=3)
        clusters = dbscan.fit_predict(embeddings_array)
        return clusters
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        return []


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
                            'anon' + str(image_clusters[idx] if idx < len(image_clusters) else ''))  # These two for loops should be done in one loop
                    else:
                        updated_user_faces.append(user_face)

                current_document_backlog = await async_images_collection.find_one({'_id': image['_id']})
                current_backlog_faces = current_document_backlog.get('backlog_faces', [])

                updated_backlog_faces = []
                for idx, user_face in enumerate(current_backlog_faces):
                    if user_face.startswith('anon'):
                        updated_backlog_faces.append(
                            'anon' + str(image_clusters[idx] if idx < len(image_clusters) else ''))  # These two for loops should be done in one loop
                    else:
                        updated_backlog_faces.append(user_face)

                update_all_faces(image['_id'], image_clusters, updated_user_faces, updated_backlog_faces)

        for image in images:
            current_document = await async_images_collection.find_one({'_id': image['_id']})
            unknown_faces = current_document.get('unknown_faces', 0)
            backlog_faces = current_document.get('backlog_faces', [])
            user_faces = current_document.get('user_faces', [])

            if unknown_faces == 0:
                continue

            for idx, user_face in enumerate(user_faces):
                if idx >= len(backlog_faces):
                    break

                backlog_face = backlog_faces[idx]
                if user_face != backlog_face and backlog_face != "anon-1":
                    update_names.delay(backlog_face, user_face)
                    backlog_faces[idx] = user_face
                    unknown_faces -= 1

            update_backlog_unknown_faces(image['_id'], unknown_faces, backlog_faces)

        embeddings, ids = fetch_all_embeddings()
        if not embeddings:
            logger.info("No embeddings found to cluster.")
            return

        clusters = cluster_embeddings(embeddings)
        update_clusters(clusters, ids)
        logger.info("Faces have been successfully grouped.")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())


@shared_task(name='face_operations.update_names')
def update_names(old_name, new_name):
    try:
        if not all(isinstance(name, str) for name in [old_name, new_name]):
            logger.error("Names must be strings")
            return False

        update_result = sync_images_collection.update_many(
            {"user_faces": old_name},
            {"$set": {
                "user_faces.$": new_name,
                "backlog_faces.$": new_name
            }}
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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def insert_many_faces(faces_records):
    sync_faces_collection.insert_many(faces_records)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def update_clusters(clusters, ids):
    for idx, cluster_id in enumerate(clusters):
        try:
            group_id = f"face{cluster_id}"
            sync_faces_collection.update_one(
                {'_id': to_object_id(ids[idx])},
                {'$set': {'group': group_id}}
            )
        except Exception as e:
            logger.error(f"Error updating clusters: {e}")
            return False
    return True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_all_embeddings():
    try:
        cursor = sync_faces_collection.find({})
        embeddings = []
        ids = []
        for doc in cursor:
            embeddings.append(np.array(doc['face_emb']))
            ids.append(doc['_id'])
        return embeddings, ids
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def update_backlog_unknown_faces(image_id, unknown_faces, backlog_faces):
    try:
        image_id = to_object_id(image_id)
        sync_images_collection.update_one(
            {'_id': image_id},
            {'$set': {'unknown_faces': unknown_faces, 'backlog_faces': backlog_faces}}
        )
        return True
    except Exception as e:
        logger.error(f"Error updating backlog faces: {e}")
        return False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def update_all_faces(image_id, image_clusters, updated_user_faces, updated_backlog_faces):
    try:
        image_id = to_object_id(image_id)
        sync_images_collection.update_one(
            {'_id': image_id},
            {'$set': {
                'auto_faces': image_clusters.tolist(),
                'user_faces': updated_user_faces,
                'backlog_faces': updated_backlog_faces
            }},
            upsert=False
        )
        return True
    except Exception as e:
        logger.error(f"Error updating all faces: {e}")
        return False
