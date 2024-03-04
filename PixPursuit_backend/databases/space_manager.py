import asyncio
from PIL import Image
from datetime import datetime
import uuid
from config.database_config import connect_to_space
from config.logging_config import setup_logging
from utils.constants import BUCKET_NAME, IMAGE_URL_PREFIX
from utils.function_utils import image_to_byte_array

logger = setup_logging(__name__)

space_client = connect_to_space()


class SpaceManager:
    def __init__(self):
        self.space_client = connect_to_space()

    @staticmethod
    def _generate_filename(extension: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:6]
        return f"{timestamp}_{unique_id}.{extension}"

    @staticmethod
    def _get_content_type(image: Image) -> str:
        if image.format == 'JPEG':
            return 'image/jpeg'
        else:
            return 'image/png'

    def put_into_space(self, image_byte_arr: bytes, filename: str, content_type: str) -> str:
        self.space_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=image_byte_arr, ContentType=content_type, ACL='public-read')
        image_url = f'{IMAGE_URL_PREFIX}{filename}'
        return image_url

    async def put_into_space_async(self, image_byte_arr: bytes, filename: str, content_type: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.put_into_space, image_byte_arr, filename, content_type)

    async def save_image_to_space(self, image: Image) -> tuple[str, str, str]:
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
        try:
            filename = file_url.split('/')[-1]
            self.space_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
            logger.info(f"Deleted {file_url} from DigitalOcean space")
        except Exception as e:
            logger.error(f"Error deleting from DigitalOcean space: {e}")
