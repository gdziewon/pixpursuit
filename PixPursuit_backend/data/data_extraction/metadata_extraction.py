"""
data/data_extraction/metadata_extraction.py

Extracts metadata from images, specifically focusing on EXIF data. This can include details like the
camera used, settings, and the date and time the photo was taken. The extracted metadata is used for
organizational, analytical, and display purposes.
"""

from PIL.ExifTags import TAGS
from PIL.Image import Image
from utils.constants import METADATA_KEYS
from config.logging_config import setup_logging

logger = setup_logging(__name__)


async def get_exif_data(image: Image) -> dict[str, str] or None:
    """
    Extract EXIF data from an image and format it according to predefined metadata keys.

    :param image: The image to process.
    :return: A dictionary containing formatted EXIF data, or None if an error occurs.
    """
    try:
        exif_data = image.getexif()
        formatted_exif_data = {}

        # Extract only specific data
        if exif_data:
            for key in METADATA_KEYS:
                tag = next((t for t, v in TAGS.items() if v == key), None)
                if tag and tag in exif_data:
                    value = exif_data[tag]

                    if key == 'DateTime':
                        value = process_exif_date(value)

                    formatted_exif_data[key] = value

        return formatted_exif_data
    except Exception as e:
        logger.error(f"Error getting exif data: {e}")
        return None


async def process_exif_date(value: str) -> str:
    """
    Process date into wanted format.
    :param value: Date extracted from metadata.
    :return: Formated date.
    """
    date_part = value.split(' ')[0]
    return date_part.replace(':', '-')