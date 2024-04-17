import heapq
import numpy as np
import dask.array as da
from concurrent.futures import ThreadPoolExecutor
from config.logging_config import setup_logging
from data.databases.mongodb.async_db.database_tools import images_collection, get_image_document
from utils.function_utils import to_object_id
import asyncio

logger = setup_logging(__name__)


class ImageSimilarity:
    def __init__(self):
        """
        Initializes the ImageSimilarity class with a ThreadPoolExecutor.
        """
        self.executor = ThreadPoolExecutor(max_workers=4)

    @staticmethod
    def _prepare_features(features: list) -> da.Array or None:
        """
        Prepares the features for similarity calculation by converting them into a Dask array.

        :param features: A list of features to be prepared.
        :return: A Dask array of the prepared features.
        """
        if not features:
            return None
        features_array = np.array(features[0])
        if features_array.size == 0 or features_array.shape == (1, 1):
            return None
        return da.from_array(features_array, chunks=(1000,))

    @staticmethod
    def _calculate_similarities(reference_features: da.Array, features_matrix: da.Array) -> np.array:
        """
        Calculates the similarities between the reference features and a matrix of features.

        :param reference_features: A Dask array of the reference features.
        :param features_matrix: A Dask array of the features' matrix.
        :return: A NumPy array of the calculated similarities.
        """
        if reference_features is None or features_matrix.shape[0] == 0:
            return np.array([])

        # Calculate cosine similarity using Dask arrays
        norm_ref = da.linalg.norm(reference_features)
        norms = da.linalg.norm(features_matrix, axis=1)
        dot_products = da.dot(features_matrix, reference_features.T)
        similarities = dot_products / (norms * norm_ref)
        return similarities.compute()

    async def _process_image_features(self, images: list) -> da.Array or None:
        """
        Processes the features of a list of images asynchronously.

        :param images: A list of images whose features are to be processed.
        :return: A Dask array of the processed features.
        """
        loop = asyncio.get_running_loop()
        # Parallelize feature preparation
        futures = [loop.run_in_executor(self.executor, self._prepare_features, img.get('features')) for img in images if img.get('features') is not None]
        features_list = await asyncio.gather(*futures)

        # Filter out None results and ensure valid feature shapes
        valid_features = [f for f in features_list if f is not None and f.shape[0] > 1]
        if not valid_features:
            return None
        return da.vstack(valid_features)

    async def find_similar_images(self, image_id: str, sample_size: int = 20) -> list[dict]:
        """
        Processes the features of a list of images asynchronously.

        :param image_id: The ID of the image for which to find similar images.
        :param sample_size: The number of images to sample for comparison.
        :return: A Dask array of the processed features.
        """
        try:
            image_document = await get_image_document(image_id)
            if not image_document or 'features' not in image_document:
                logger.warning(f"No features found for image ID: {image_id}")
                return []

            reference_features = self._prepare_features(image_document['features'])
            if reference_features is None:
                return []

            # Get a sample of images to compare
            sample_images = await self._get_sample_images(image_id, sample_size)
            features_matrix = await self._process_image_features(sample_images)
            if features_matrix is None:
                return []

            # Calculate similarities between the reference features and the sample images
            similarities = self._calculate_similarities(da.asarray(reference_features), features_matrix)

            # Find top similar images using a heap
            top_images = []
            for score, img in zip(similarities, sample_images):
                if score is not None:
                    heapq.heappush(top_images, (score, str(img['_id']), img.get('thumbnail_url')))
                if len(top_images) > sample_size:
                    heapq.heappop(top_images)

            top_images.sort(reverse=True, key=lambda x: x[0])
            return top_images
        except Exception as e:
            logger.error(f"Unhandled exception in find_similar_images: {e}")
            return []

    @staticmethod
    async def _get_sample_images(image_id: str, limit: int) -> list:
        """
        Gets a sample of images from the database.

        :param image_id: The ID of the image to exclude from the sample.
        :param limit: The maximum number of images to include in the sample.
        :return: A list of the sampled images.
        """
        oid = to_object_id(image_id)
        if oid is None:
            logger.error("Invalid ObjectId")
            return []

        total_docs = await images_collection.count_documents({})
        if total_docs == 0:
            return []

        size = max(limit, total_docs // 70)
        pipeline = [
            {'$match': {'_id': {'$ne': oid}}},
            {'$sample': {'size': size}},
            {'$project': {'features': 1, 'thumbnail_url': 1}}
        ]
        cursor = images_collection.aggregate(pipeline)
        return await cursor.to_list(length=size)
