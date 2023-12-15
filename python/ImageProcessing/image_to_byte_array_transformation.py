import asyncio
from io import BytesIO
from PIL import Image


def image_to_byte_array(image: Image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


async def image_to_byte_array_async(image: Image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, image_to_byte_array, image)
