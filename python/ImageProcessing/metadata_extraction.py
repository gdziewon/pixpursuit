import asyncio
from PIL.ExifTags import TAGS


def get_exif_data(image):
    exif_data = image._getexif()

    if exif_data:
        formatted_exif_data = {}
        for key, value in exif_data.items():
            if isinstance(value, bytes):
                value = value.decode(errors='ignore')
            elif not isinstance(value, (int, float, str, list, dict, tuple)):
                value = str(value)
            formatted_exif_data[TAGS.get(key, key)] = value
        return formatted_exif_data
    return {}


async def get_exif_data_async(image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_exif_data, image)
