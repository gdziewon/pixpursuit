from databases.database_tools import get_image_document, images_collection, get_root_id
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from config.logging_config import setup_logging
from bson.objectid import ObjectId
from utils.constants import WEIGHTS

logger = setup_logging(__name__)
tfidf_vectorizer = TfidfVectorizer()


async def find_similar_images(image_id, limit=20):
    logger.info(f"Finding similar images for image ID: {image_id}")
    input_image = await get_image_document(image_id)
    if not input_image:
        logger.warning(f"No input image found for image ID: {image_id}")
        return []

    cursor = images_collection.find({'_id': {'$ne': ObjectId(image_id)}}, {
        'features': 1, 'user_tags': 1, 'user_faces': 1, 'description': 1,
        'album_id': 1, 'auto_faces': 1, 'auto_tags': 1, 'detected_objects': 1,
        'added_by': 1, 'thumbnail_url': 1
    })

    try:
        similarities = []
        async for img in cursor:
            score = 0
            score += WEIGHTS['features'] * await feature_similarity(input_image['features'], img['features'])
            score += WEIGHTS['user_tags'] * await jaccard_similarity(input_image['user_tags'], img['user_tags'])
            score += WEIGHTS['user_faces'] * await face_similarity(input_image['user_faces'], img['user_faces'])
            score += WEIGHTS['description'] * await description_similarity(input_image['description'], img['description'])
            score += WEIGHTS['album_id'] * await album_similarity(input_image['album_id'], img['album_id'])
            score += WEIGHTS['auto_faces'] * await face_similarity(input_image['auto_faces'], img['auto_faces'])
            score += WEIGHTS['auto_tags'] * await jaccard_similarity(input_image['auto_tags'], img['auto_tags'])
            score += WEIGHTS['detected_objects'] * await jaccard_similarity(input_image['detected_objects'], img['detected_objects'])
            score += WEIGHTS['added_by'] * await added_by_similarity(input_image['added_by'], img['added_by'])

            similarities.append({'_id': str(img['_id']), 'thumbnail_url': img['thumbnail_url'], 'score': score})
    except Exception as e:
        logger.error(f"Error during similarity computation for image ID: {image_id}: {e}")
        return []

    similarities.sort(key=lambda x: x['score'], reverse=True)
    return similarities[:limit]


async def feature_similarity(features1, features2):
    if not features1 or not features2:
        return 0.0

    features1 = np.array(features1)
    features2 = np.array(features2)

    features1 = features1.reshape(1, -1)
    features2 = features2.reshape(1, -1)

    similarity = cosine_similarity(features1, features2)[0][0]
    return similarity


async def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0

    set1 = set(set1)
    set2 = set(set2)

    intersection = set1.intersection(set2)
    union = set1.union(set2)

    if not union:
        return 1.0

    similarity = len(intersection) / len(union)
    return similarity


async def face_similarity(faces1, faces2):
    set1 = (set(faces1) - {'anon-1', '-1'}) if faces1 else set()
    set2 = (set(faces2) - {'anon-1', '-1'}) if faces2 else set()

    return await jaccard_similarity(set1, set2)


async def description_similarity(description1, description2):
    if not description1 or not description2:
        return 0.0

    descriptions = [description1, description2]

    if all(tfidf_vectorizer.build_analyzer()(desc) == [] for desc in descriptions):
        return 0.0

    tfidf_matrix = tfidf_vectorizer.fit_transform(descriptions)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return similarity


async def album_similarity(album_id1, album_id2):
    root_id = await get_root_id()
    if album_id1 != root_id and album_id1 == album_id2:
        return 1
    else:
        return 0


async def added_by_similarity(added_by1, added_by2):
    return 1 if added_by1 == added_by2 else 0
