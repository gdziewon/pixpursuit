import asyncio
import heapq
from data.databases.database_tools import get_image_document, images_collection
from config.logging_config import setup_logging
from utils.function_utils import to_object_id
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse

logger = setup_logging(__name__)


class ImageSimilarity:
    def __init__(self):
        self.input_image = None
        self.input_img_vecs = None

    @staticmethod
    def _get_pipeline(image_id: str, sample_size: int) -> list[dict]:
        return [
            {'$match': {'_id': {'$ne': image_id}}},
            {'$sample': {'size': sample_size}},
            {'$project': {'user_tags': 1, 'user_faces': 1, 'album_id': 1, 'auto_faces': 1, 'auto_tags': 1,
                          'added_by': 1, 'thumbnail_url': 1}}
        ]

    @staticmethod
    async def _get_sample_images(image_id: str, limit: int) -> list[dict] or None:
        try:
            image_id = to_object_id(image_id)
            if not image_id:
                return []

            total_docs = await images_collection.count_documents({})
            sample_size = max(limit, total_docs // 10)

            # fetches a random sample of approximately 1/10 of the collection documents
            pipeline = ImageSimilarity._get_pipeline(image_id, sample_size)

            cursor = images_collection.aggregate(pipeline)
            return await cursor.to_list(length=sample_size)
        except Exception as e:
            logger.error(f"Error getting cursor: {e}")
            return []

    async def find_similar_images(self, image_id: str, limit: int = 20) -> list[dict]:
        logger.info(f"Finding similar images for image ID: {image_id}")

        try:
            self.input_image = await get_image_document(image_id)
            if not self.input_image:
                logger.warning(f"No input image found for image ID: {image_id}")
                return []

            images = await ImageSimilarity._get_sample_images(image_id, limit)
            semaphore = asyncio.Semaphore(10)

            async def task(img):
                async with semaphore:
                    return await self._calculate_other_similarities(img)

            tasks = [task(img) for img in images]
            total_scores = await asyncio.gather(*tasks)

            extracted_data = await ImageSimilarity._extract_thumbnails_and_ids(images, total_scores, limit)
            return extracted_data

        except Exception as e:
            logger.error(f"Error finding similar images: {e}")
            return []

    @staticmethod
    async def _get_limited_results(images: list[dict], total_scores: tuple, limit: int) -> list[dict]:
        similarities_with_ids = []
        for img, score in zip(images, total_scores):
            if len(similarities_with_ids) < limit:
                heapq.heappush(similarities_with_ids, (-score, str(img['_id']), img['thumbnail_url']))
            else:
                heapq.heappushpop(similarities_with_ids, (-score, str(img['_id']), img['thumbnail_url']))

        limited_results = heapq.nlargest(limit, similarities_with_ids)
        return limited_results

    @staticmethod
    async def _extract_thumbnails_and_ids(images: list[dict], total_scores: tuple, limit: int) -> list[dict]:
        limited_results = await ImageSimilarity._get_limited_results(images, total_scores, limit)
        return [{'_id': _id, 'thumbnail_url': thumbnail_url, 'score': -score}
                for score, _id, thumbnail_url in limited_results]

    async def _calculate_other_similarities(self, image2: dict) -> float:
        if not self.input_image or not self.input_img_vecs:
            return 0.0

        score = sum(
            await self._cosine_similarity(self.input_image.get(feature, []), image2.get(feature, []))
            for feature in ['user_tags', 'user_faces', 'auto_faces', 'auto_tags']
        )

        score += self._standard_similarity(self.input_image.get('album_id', ''), image2.get('album_id', ''))
        score += self._standard_similarity(self.input_image.get('added_by', ''), image2.get('added_by', ''))

        return score

    async def _cosine_similarity(self, list1: list, list2: list) -> float:
        if not list1 or not list2:
            return 0.0

        list1_key = tuple(list1)
        if list1_key not in self.input_img_vecs:
            self.input_img_vecs[list1_key] = sparse.csr_matrix(list1)

        vec1 = self.input_img_vecs[list1_key]
        vec2 = sparse.csr_matrix(list2)

        return cosine_similarity(vec1, vec2)[0][0]

    @staticmethod
    def _standard_similarity(input_str: str, other_str: str) -> float:
        return 1.0 if input_str == other_str else 0.0
