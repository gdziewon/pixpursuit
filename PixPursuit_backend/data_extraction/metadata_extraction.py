import asyncio
from PIL.ExifTags import TAGS
from utils.constants import METADATA_KEYS


def get_exif_data(image):
    exif_data = image._getexif()
    formatted_exif_data = {}

    if exif_data:
        for key in METADATA_KEYS:
            tag = next((t for t, v in TAGS.items() if v == key), None)
            if tag and tag in exif_data:
                value = exif_data[tag]
                if key == 'DateTime':
                    date_part = value.split(' ')[0]
                    formatted_date = date_part.replace(':', '-')
                    formatted_exif_data[key] = formatted_date
                else:
                    formatted_exif_data[key] = value

    return formatted_exif_data


async def get_exif_data_async(image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_exif_data, image)
