import asyncio
from io import BytesIO
from PIL import Image
from datetime import datetime
import uuid
from setup import connect_to_space
from logging_config import setup_logging

logger = setup_logging(__name__)

space_client = connect_to_space()
space_name = 'pixpursuit'


def generate_filename(extension):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    return f"{timestamp}_{unique_id}.{extension}"


def get_content_type(image):
    if image.format == 'JPEG':
        return 'image/jpeg'
    else:
        return 'image/png'


def put_into_space(image_byte_arr, filename, content_type):
    space_client.put_object(Bucket=space_name, Key=filename, Body=image_byte_arr, ContentType=content_type, ACL='public-read')
    image_url = f'https://{space_name}.ams3.digitaloceanspaces.com/pixpursuit/{filename}'
    return image_url


async def put_into_space_async(image_byte_arr, filename, content_type):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, put_into_space, image_byte_arr, filename, content_type)


def image_to_byte_array(image: Image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


async def save_image_to_space(image: Image):
    img_byte_arr = image_to_byte_array(image)
    content_type = get_content_type(image)
    extension = content_type.split('/')[-1]
    filename = generate_filename(extension)
    image.thumbnail((300, 300))
    thumbnail_byte_arr = image_to_byte_array(image)
    image_url = await put_into_space_async(img_byte_arr, filename, content_type)
    thumbnail_url = await put_into_space_async(thumbnail_byte_arr, f'thumbnail{filename}', content_type)
    return image_url, thumbnail_url


async def delete_image_from_space(file_url: str):
    try:
        filename = file_url.split('/')[-1]
        space_client.delete_object(Bucket=space_name, Key=filename)
        logger.info(f"Deleted {file_url} from DigitalOcean space")
    except Exception as e:
        logger.error(f"Error deleting from DigitalOcean space: {e}")
