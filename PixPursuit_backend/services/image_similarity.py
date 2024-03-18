from data.databases.database_tools import get_image_document, images_collection, get_root_id
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from config.logging_config import setup_logging
from utils.constants import WEIGHTS
from utils.function_utils import to_object_id

logger = setup_logging(__name__)


class ImageSimilarity:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer()

    @staticmethod
    async def _get_cursor(image_id: str) -> list[dict] or None:
        image_id = to_object_id(image_id)
        if not image_id:
            return []

        return images_collection.find({'_id': {'$ne': image_id}}, {
            'features': 1, 'user_tags': 1, 'user_faces': 1,
            'album_id': 1, 'auto_faces': 1, 'auto_tags': 1,
            'added_by': 1, 'thumbnail_url': 1
        })

    @staticmethod
    async def find_similar_images(image_id: str, limit: int = 20) -> list[dict]:
        logger.info(f"Finding similar images for image ID: {image_id}")
        input_image = await get_image_document(image_id)
        if not input_image or 'features' not in input_image:
            logger.warning(f"No input image or features found for image ID: {image_id}")
            return []

        cursor = await ImageSimilarity._get_cursor(image_id)
        images = await ImageSimilarity._pre_filter_images(input_image, cursor)

        feature_vectors = np.array([img['features'] for img in images if 'features' in img])
        input_features = np.array(input_image['features']).reshape(1, -1)
        feature_similarities = cosine_similarity(input_features, feature_vectors)[0]

        similarities_with_ids = []
        for i, img in enumerate(images):
            if 'features' in img:
                feature_similarity_score = feature_similarities[i]
            else:
                feature_similarity_score = 0.0

            other_similarity_score = await ImageSimilarity._calculate_other_similarities(input_image, img)

            total_score = WEIGHTS['features'] * feature_similarity_score + other_similarity_score

            similarities_with_ids.append((str(img['_id']), img['thumbnail_url'], total_score))

        limited_results = sorted(similarities_with_ids, key=lambda x: x[2], reverse=True)[:limit]
        return [{'_id': res[0], 'thumbnail_url': res[1], 'score': res[2]} for res in limited_results]

    @staticmethod
    async def _pre_filter_images(input_image, cursor):
        pre_filtered_images = []
        for img in cursor:
            if ImageSimilarity._basic_criteria_met(input_image, img):
                pre_filtered_images.append(img)
        return pre_filtered_images

    @staticmethod
    def _basic_criteria_met(image1, image2):
        if not set(image1['user_tags']).intersection(set(image2['user_tags'])) or \
                not set(image1['auto_tags']).intersection(set(image2['auto_tags'])) or \
                not set(image1['user_faces']).intersection(set(image2['user_faces'])) or \
                not set(image1['auto_faces']).intersection(set(image2['auto_faces'])):
            return False
        return True

    @staticmethod
    async def _calculate_other_similarities(image1: dict, image2: dict) -> float:
        score = 0.0
        score += WEIGHTS['user_tags'] * await ImageSimilarity._jaccard_similarity(image1['user_tags'],                                                                      image2['user_tags'])
        score += WEIGHTS['user_faces'] * await ImageSimilarity._face_similarity(image1['user_faces'],                                                                     image2['user_faces'])
        score += WEIGHTS['album_id'] * await ImageSimilarity._album_similarity(image1['album_id'], image2['album_id'])
        score += WEIGHTS['auto_faces'] * await ImageSimilarity._face_similarity(image1['auto_faces'],                                                                       image2['auto_faces'])
        score += WEIGHTS['auto_tags'] * await ImageSimilarity._jaccard_similarity(image1['auto_tags'],                                                                         image2['auto_tags'])
        score += WEIGHTS['added_by'] * await ImageSimilarity._added_by_similarity(image1['added_by'],
                                                                                  image2['added_by'])
        return score

    @staticmethod
    async def _jaccard_similarity(set1: set, set2: set) -> float:
        if not set1 or not set2:
            return 0.0

        try:
            set1 = set(set1)
            set2 = set(set2)
            intersection = set1.intersection(set2)
            union = set1.union(set2)

            similarity = len(intersection) / len(union)
            return similarity
        except Exception as e:
            logger.error(f"Error during Jaccard similarity computation: {e}")
            return 0.0

    @staticmethod
    async def _face_similarity(faces1: list[str], faces2: list[str]) -> float:
        set1 = (set(faces1) - {'anon-1', '-1'}) if faces1 else set()
        set2 = (set(faces2) - {'anon-1', '-1'}) if faces2 else set()

        return await ImageSimilarity._jaccard_similarity(set1, set2)

    @staticmethod
    async def _album_similarity(album_id1: str, album_id2: str) -> float:
        root_id = await get_root_id()
        if album_id1 != root_id and album_id1 == album_id2:
            return 1.0
        else:
            return 0.0

    @staticmethod
    async def _added_by_similarity(added_by1: str, added_by2: str) -> float:
        return 1 if added_by1 == added_by2 else 0.0
