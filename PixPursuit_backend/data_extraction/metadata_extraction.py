from PIL.ExifTags import TAGS
from PIL.Image import Image
from utils.constants import METADATA_KEYS
from config.logging_config import setup_logging

logger = setup_logging(__name__)


async def get_exif_data(image: Image) -> dict[str, str] or None:
    try:
        exif_data = image.getexif()
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
    except Exception as e:
        logger.error(f"Error getting exif data: {e}")
        return None
