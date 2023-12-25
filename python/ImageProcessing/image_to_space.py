import asyncio
from io import BytesIO
from PIL import Image
from datetime import datetime
import uuid
from setup import connect_to_space

space_client = connect_to_space()
space_name = 'pixpursuit'


def generate_filename(extension):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    return f"{timestamp}_{unique_id}.{extension}"


def get_content_type(image):
    if image.format == 'JPEG':
        return 'image/jpeg'
    elif image.format == 'PNG':
        return 'image/png'
    else:
        return 'application/octet-stream'


def put_into_space(image_byte_arr, filename, content_type):
    space_client.put_object(Bucket=space_name, Key=filename, Body=image_byte_arr, ContentType=content_type)
    image_url = f'https://{space_name}.ams3.digitaloceanspaces.com/{filename}'
    return image_url


async def put_into_space_async(image_byte_arr, filename, content_type):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, put_into_space, image_byte_arr, filename, content_type)


def image_to_byte_array(image: Image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    content_type = get_content_type(image)
    extension = content_type.split('/')[-1]
    filename = generate_filename(extension)
    return img_byte_arr, filename, content_type


async def image_to_space_async(image: Image):
    img_byte_arr, filename, content_type = image_to_byte_array(image)
    image_url = await put_into_space_async(img_byte_arr, filename, content_type)
    return image_url
