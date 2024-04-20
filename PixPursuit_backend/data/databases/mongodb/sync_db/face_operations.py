from bson import ObjectId
from config.database_config import connect_to_mongodb
from config.logging_config import setup_logging
from celery import shared_task
import numpy as np
from sklearn.cluster import DBSCAN
from tenacity import retry, stop_after_attempt, wait_fixed
from utils.function_utils import to_object_id
from pymongo import DeleteOne
from sklearn.neighbors import BallTree
from utils.constants import (
    GROUP_FACES_TASK, DELETE_FACES_TASK, UPDATE_NAMES_TASK, MAIN_QUEUE, BEAT_QUEUE,
    DBSCAN_EPS, DBSCAN_MIN_SAMPLES, FACE_DELETE_THRESHOLD)

logger = setup_logging(__name__)

sync_images_collection, _, sync_faces_collection, _, _ = connect_to_mongodb(async_mode=False)
dbscan = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES)


def cluster_embeddings(embeddings: list[np.ndarray]) -> np.ndarray or None:
    """
   Clusters the given face embeddings using the DBSCAN algorithm.

   :param embeddings: A list of face embeddings to cluster.
   :return: An array of cluster labels for each embedding, or None if an error occurs.
   """
    try:
        embeddings_array = np.array(embeddings)
        clusters = dbscan.fit_predict(embeddings_array)
        return clusters
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_images() -> list[dict]:
    """
    Fetches all image documents from the sync_images_collection where the 'embeddings' field exists and is not empty.

    :return: A list of image documents, or an empty list if an error occurs.
    """
    try:
        cursor = sync_images_collection.find({'embeddings': {'$exists': True, '$not': {'$size': 0}}})
        return list(cursor)
    except Exception as e:
        logger.error(f"Error fetching images: {e}")
        return []


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def process_images(images: list[dict]) -> None:
    """
    Processes a list of image documents by clustering their embeddings and updating their faces.

    :param images: A list of image documents to process.
    """
    try:
        all_embeddings = [emb for image in images for emb in image['embeddings']]

        if not all_embeddings:
            logger.info("No embeddings found for clustering.")
            return

        embeddings_array = np.array(all_embeddings)
        clustering = dbscan.fit(embeddings_array)

        label_idx = 0
        for image in images:
            current_document = sync_images_collection.find_one({'_id': image['_id']})
            unknown_faces = current_document.get('unknown_faces', 0)
            backlog_faces = current_document.get('backlog_faces', [])
            user_faces = current_document.get('user_faces', [])

            if unknown_faces != 0:
                for idx, user_face in enumerate(user_faces):
                    if idx >= len(backlog_faces):
                        break

                    backlog_face = backlog_faces[idx]
                    if user_face != backlog_face and backlog_face != "anon-1":
                        update_names.delay(backlog_face, user_face)
                        backlog_faces[idx] = user_face
                        unknown_faces -= 1

                update_backlog_unknown_faces(image['_id'], unknown_faces, backlog_faces)

            num_embeddings = len(image['embeddings'])
            if num_embeddings > 0:
                image_clusters = clustering.labels_[label_idx:label_idx + num_embeddings]
                label_idx += num_embeddings
                update_faces(image, image_clusters)
    except Exception as e:
        logger.error(f"Error in process_images: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def update_faces(image: dict, image_clusters: np.ndarray) -> None:
    """
    Updates the faces of a given image document in the sync_images_collection.

    :param image: The image document to update.
    :param image_clusters: The array of cluster labels for each face embedding in the image.
    """
    try:
        current_document = sync_images_collection.find_one({'_id': image['_id']})
        current_user_faces = current_document.get('user_faces', [])
        current_backlog_faces = current_document.get('backlog_faces', [])

        updated_user_faces, updated_backlog_faces = update_user_and_backlog_faces(current_user_faces, current_backlog_faces, image_clusters)
        update_all_faces(image['_id'], image_clusters, updated_user_faces, updated_backlog_faces)
    except Exception as e:
        logger.error(f"Error in update_faces: {e}")
        return None


def update_user_and_backlog_faces(current_faces: list, current_backlog_faces: list[str],
                                  image_clusters: np.ndarray) -> tuple[list, list] or None:
    """
    Updates the user and backlog faces of a given image document based on the cluster labels.

    :param current_faces: The current user faces of the image document.
    :param current_backlog_faces: The current backlog faces of the image document.
    :param image_clusters: The array of cluster labels for each face embedding in the image.
    :return: A tuple containing the updated user faces and backlog faces, or None if an error occurs.
    """
    try:
        updated_faces = []
        updated_backlog_faces = []
        for idx, (user_face, backlog_face) in enumerate(zip(current_faces, current_backlog_faces)):
            if user_face.startswith('anon'):
                updated_faces.append('anon' + str(image_clusters[idx] if idx < len(image_clusters) else ''))
            else:
                updated_faces.append(user_face)

            if backlog_face.startswith('anon'):
                updated_backlog_faces.append('anon' + str(image_clusters[idx] if idx < len(image_clusters) else ''))
            else:
                updated_backlog_faces.append(backlog_face)

        return updated_faces, updated_backlog_faces
    except Exception as e:
        logger.error(f"Error in update_user_and_backlog_faces: {e}")
        return None


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def insert_many_faces(faces_records: list[dict]) -> None:
    """
    Inserts multiple face records into the sync_faces_collection.

    :param faces_records: A list of face records to insert.
    """
    sync_faces_collection.insert_many(faces_records)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def update_clusters(clusters: np.ndarray, ids: list[ObjectId]) -> bool:
    """
    Updates the cluster labels of the face documents in the sync_faces_collection.

    :param clusters: The array of cluster labels for each face embedding.
    :param ids: The list of IDs of the face documents to update.
    :return: True if the update was successful, False otherwise.
    """
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
def fetch_all_embeddings() -> tuple[list[np.ndarray], list[ObjectId]] or None:
    """
    Fetches all face embeddings and their corresponding IDs from the sync_faces_collection.

    :return: A tuple containing a list of face embeddings and a list of their corresponding IDs, or None if an error occurs.
    """
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
def update_backlog_unknown_faces(image_id: str, unknown_faces: int, backlog_faces: list[str]) -> bool:
    """
    Updates the 'unknown_faces' and 'backlog_faces' fields of a given image document in the sync_images_collection.

    :param image_id: The ID of the image document to update.
    :param unknown_faces: The updated count of unknown faces.
    :param backlog_faces: The updated list of backlog faces.
    :return: True if the update was successful, False otherwise.
    """
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
def update_all_faces(image_id: str, image_clusters: np.ndarray, updated_user_faces: list[str],
                     updated_backlog_faces: list) -> bool:
    """
    Updates the 'auto_faces', 'user_faces', and 'backlog_faces' fields of a given image document in the sync_images_collection.

    :param image_id: The ID of the image document to update.
    :param image_clusters: The array of cluster labels for each face embedding in the image.
    :param updated_user_faces: The updated list of user faces.
    :param updated_backlog_faces: The updated list of backlog faces.
    :return: True if the update was successful, False otherwise.
    """
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


@shared_task(name=GROUP_FACES_TASK, queue=BEAT_QUEUE)
def group_faces() -> None:
    """
    Groups faces by fetching all images, processing them, and then clustering their embeddings.

    This function is a Celery task that runs on the BEAT_QUEUE.
    """
    images = fetch_images()
    process_images(images)

    embeddings, ids = fetch_all_embeddings()
    if not embeddings:
        logger.info("No embeddings found to cluster.")
        return

    clusters = cluster_embeddings(embeddings)
    update_clusters(clusters, ids)
    logger.info("Faces have been successfully grouped.")


@shared_task(name=UPDATE_NAMES_TASK, queue=MAIN_QUEUE)
def update_names(old_name: str, new_name: str) -> bool:
    """
    Updates the names of faces in the sync_images_collection.

    :param old_name: The old name of the face.
    :param new_name: The new name of the face.
    :return: True if the update was successful, False otherwise.
    """
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
        logger.error(f"Error in update_names: {e}")
        return False


@shared_task(name=DELETE_FACES_TASK, queue=MAIN_QUEUE)
def delete_faces_associated_with_images(image_ids: list) -> bool:
    """
    Deletes faces associated with given images from the sync_faces_collection.

    :param image_ids: The list of IDs of the images whose associated faces are to be deleted.
    :return: True if the deletion was successful, False otherwise.
    """
    delete_operations = []

    image_embeddings = {}
    for image_id in image_ids:
        image_id = to_object_id(image_id)
        image_doc = sync_images_collection.find_one({'_id': image_id})
        if image_doc is not None:
            image_embeddings[image_id] = image_doc.get('embeddings', [])

    face_docs = list(sync_faces_collection.find({}))
    face_embeddings = [doc.get('face_emb', []) for doc in face_docs]

    tree = BallTree(face_embeddings)

    for image_id, embeddings in image_embeddings.items():
        for emb in embeddings:
            indices = tree.query_radius([emb], r=FACE_DELETE_THRESHOLD)

            for index in indices[0]:
                delete_operations.append(DeleteOne({'_id': to_object_id(face_docs[index]['_id'])}))

    if delete_operations:
        try:
            delete_result = sync_faces_collection.bulk_write(delete_operations)
            logger.info(f"Successfully deleted {delete_result.deleted_count} faces.")
        except Exception as e:
            logger.error(f"Error performing bulk delete operation: {e}")
            return False

    return True
