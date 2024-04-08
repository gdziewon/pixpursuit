"""
services/image_similarity.py

Defines a class for calculating similarity scores between images stored in a database.
Uses features like user tags, faces, and other metadata to determine similarity,
leveraging cosine similarity for vectorized features.
"""

import asyncio
import heapq
from data.databases.mongodb.async_db.database_tools import get_image_document, images_collection
from config.logging_config import setup_logging
from utils.function_utils import to_object_id
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse

logger = setup_logging(__name__)


class ImageSimilarity:
    """
    Class to calculate similarity between images based on various features like tags and faces.
    """
    def __init__(self):
        self.input_image = None
        self.input_img_vecs = None

    @staticmethod
    def _get_pipeline(image_id: str, sample_size: int) -> list[dict]:
        """
        Creates an aggregation pipeline for MongoDB to fetch a sample of images.

        :param image_id: The ID of the image to exclude from the sample.
        :param sample_size: The number of images to sample.
        :return: An aggregation pipeline list.
        """
        return [
            {'$match': {'_id': {'$ne': image_id}}},
            {'$sample': {'size': sample_size}},
            {'$project': {'user_tags': 1, 'user_faces': 1, 'album_id': 1, 'auto_faces': 1, 'auto_tags': 1,
                          'added_by': 1, 'thumbnail_url': 1}}
        ]

    @staticmethod
    async def _get_sample_images(image_id: str, limit: int) -> list[dict] or None:
        """
        Fetches a sample of images from the database excluding the specified image.

        :param image_id: The ID of the image to exclude.
        :param limit: The minimum number of images to fetch.
        :return: A list of image documents.
        """
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
        """
        Finds images similar to the specified image.

        :param image_id: The ID of the image to find similarities for.
        :param limit: The number of similar images to return.
        :return: A list of similar images with their IDs and thumbnail URLs.
        """

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
                    return await self._calculate_similarity(img)

            tasks = [task(img) for img in images]
            total_scores = await asyncio.gather(*tasks)

            extracted_data = await ImageSimilarity._extract_thumbnails_and_ids(images, total_scores, limit)
            return extracted_data

        except Exception as e:
            logger.error(f"Error finding similar images: {e}")
            return []

    @staticmethod
    async def _get_limited_results(images: list[dict], total_scores: tuple, limit: int) -> list[dict]:
        """
        Limits the results to a specified number based on the highest similarity scores.

        This method uses a min-heap to efficiently keep track of the top similarity scores and
        their corresponding images. It ensures that only the top 'limit' number of similar images
        are returned.

        :param images: A list of image dictionaries to evaluate.
        :param total_scores: A tuple containing the similarity scores for each image.
        :param limit: The maximum number of results to return.
        :return: A list of dictionaries each containing the image ID and thumbnail URL of the top
                 images, sorted by their similarity scores in descending order.
        """
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
        """
        Extracts thumbnail URLs and IDs from the list of images based on similarity scores.

        :param images: The list of image documents.
        :param total_scores: The list of similarity scores corresponding to the images.
        :param limit: The number of top results to extract.
        :return: A list of dictionaries containing image IDs and thumbnail URLs.
        """
        limited_results = await ImageSimilarity._get_limited_results(images, total_scores, limit)
        return [{'_id': _id, 'thumbnail_url': thumbnail_url, 'score': -score}
                for score, _id, thumbnail_url in limited_results]

    async def _calculate_similarity(self, image2: dict) -> float:
        """
        Calculates the similarity score between the input image and another image.

        :param image2: The other image document to compare with the input image.
        :return: The similarity score.
        """
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
        """
        Computes the cosine similarity between two lists representing feature vectors.

        Converts the lists into sparse matrix vectors and calculates their cosine similarity.
        This is used as a part of the overall similarity calculation between two images.

        :param list1: A list representing a feature vector of the input image.
        :param list2: A list representing the same feature vector of another image.
        :return: A float representing the cosine similarity between the two vectors.
        """
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
        """
        Calculates a simple similarity score based on string equality.

        :param input_str: The first string for comparison.
        :param other_str: The second string for comparison.
        :return: 1.0 if the strings are equal, otherwise 0.0.
        """
        return 1.0 if input_str == other_str else 0.0
