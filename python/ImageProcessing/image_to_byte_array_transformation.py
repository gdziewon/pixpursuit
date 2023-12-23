import asyncio
from io import BytesIO
from PIL import Image
from datetime import datetime
import uuid


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


def image_to_byte_array(image: Image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    content_type = get_content_type(image)
    extension = content_type.split('/')[-1]
    filename = generate_filename(extension)
    return img_byte_arr, content_type, filename


async def image_to_byte_array_async(image: Image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, image_to_byte_array, image)
