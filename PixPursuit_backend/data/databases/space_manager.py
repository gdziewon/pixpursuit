"""
data/databases/space_manager.py

Handles operations related to storing and managing images in a DigitalOcean Space,
including uploading, generating thumbnails, and deleting images. This module provides
both synchronous and asynchronous methods for interaction with the cloud storage.
"""

import asyncio
from PIL import Image
from datetime import datetime
import uuid
from config.database_config import connect_to_space
from config.logging_config import setup_logging
from utils.constants import BUCKET_NAME, IMAGE_URL_PREFIX
from utils.function_utils import image_to_byte_array

logger = setup_logging(__name__)


class SpaceManager:
    """
    Manages the storage of images in a DigitalOcean Space.
    """
    def __init__(self):
        """
        Initializes the SpaceManager with a connection to DigitalOcean Space.
        """
        self.space_client = connect_to_space()

    @staticmethod
    def _generate_filename(extension: str) -> str:
        """
        Generates a unique filename using the current timestamp and a UUID.

        :param extension: The file extension to use for the filename.
        :return: A unique filename string.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:6]
        return f"{timestamp}_{unique_id}.{extension}"

    @staticmethod
    def _get_content_type(image: Image) -> str:
        """
        Determines the content type of image based on its format.

        :param image: The image to check.
        :return: The content type of the image.
        """
        if image.format == 'JPEG':
            return 'image/jpeg'
        else:
            return 'image/png'

    def put_into_space(self, image_byte_arr: bytes, filename: str, content_type: str) -> str:
        """
        Synchronously uploads an image to DigitalOcean Space.

        :param image_byte_arr: The byte array of the image to upload.
        :param filename: The filename to use in the storage.
        :param content_type: The content type of the image.
        :return: The URL of the uploaded image.
        """
        self.space_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=image_byte_arr, ContentType=content_type, ACL='public-read')
        image_url = f'{IMAGE_URL_PREFIX}{filename}'
        return image_url

    async def put_into_space_async(self, image_byte_arr: bytes, filename: str, content_type: str) -> str:
        """
        Asynchronously uploads an image to DigitalOcean Space.

        :param image_byte_arr: The byte array of the image to upload.
        :param filename: The filename to use in the storage.
        :param content_type: The content type of the image.
        :return: The URL of the uploaded image.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.put_into_space, image_byte_arr, filename, content_type)

    async def save_image_to_space(self, image: Image) -> tuple[str, str, str]:
        """
        Processes, creates a thumbnail, and uploads an image and its thumbnail to DigitalOcean Space.

        :param image: The image to process and upload.
        :return: A tuple containing the URLs of the image and its thumbnail, and the filename used.
        """
        img_byte_arr = await image_to_byte_array(image)
        content_type = SpaceManager._get_content_type(image)
        extension = content_type.split('/')[-1]
        filename = SpaceManager._generate_filename(extension)

        image.thumbnail((300, 300))
        thumbnail_byte_arr = await image_to_byte_array(image)

        image_url = await self.put_into_space_async(img_byte_arr, filename, content_type)
        thumbnail_url = await self.put_into_space_async(thumbnail_byte_arr, f'thumbnail{filename}', content_type)
        return image_url, thumbnail_url, filename

    async def delete_image_from_space(self, file_url: str) -> None:
        """
        Deletes an image from DigitalOcean Space.

        :param file_url: The URL of the file to delete.
        """
        try:
            filename = file_url.split('/')[-1]
            self.space_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
            logger.info(f"Deleted {file_url} from DigitalOcean space")
        except Exception as e:
            logger.error(f"Error deleting from DigitalOcean space: {e}")

    async def get_image_from_space(self, filename: str):
        """
        Returns an image from DigitalOcean Space.
        :param filename: Filename associated with the image.
        :return: Answer from the DigitalOcean Space client.
        """
        return self.space_client.get_object(Bucket=BUCKET_NAME, Key=filename)
