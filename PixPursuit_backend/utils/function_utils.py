from bson import ObjectId
from utils.constants import ALLOWED_EXTENSIONS, PK_GALLERY_URL
from config.logging_config import setup_logging
from PIL import Image
from io import BytesIO

logger = setup_logging(__name__)


def is_allowed_file(filename: str) -> bool:
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_allowed_url(url: str) -> bool:
    return url.startswith(PK_GALLERY_URL)


def to_object_id(id_str: ObjectId or str) -> ObjectId or None:
    try:
        id_obj = ObjectId(id_str)
        return id_obj
    except Exception as e:
        logger.error(f"Failed to convert {id_str} to ObjectId: {e}")
        return None


async def image_to_byte_array(image: Image) -> bytes or None:
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
