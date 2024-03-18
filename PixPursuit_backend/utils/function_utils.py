import os
from bson import ObjectId
from fastapi import UploadFile
from utils.constants import ALLOWED_EXTENSIONS, PK_GALLERY_URL
from config.logging_config import setup_logging
from PIL import Image
from io import BytesIO
from utils.exceptions import prepare_image_files_exception

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


async def convert_to_upload_file(save_dir: str) -> list[UploadFile]:
    try:
        image_filenames = os.listdir(save_dir)
        image_files = []
        for filename in image_filenames:
            image_path = os.path.join(save_dir, filename)
            with open(image_path, 'rb') as file:
                contents = file.read()
            upload_file = UploadFile(filename=filename, file=BytesIO(contents))
            image_files.append(upload_file)

        return image_files
    except Exception as e:
        logger.error(f"Failed to prepare image files: {e}")
        raise prepare_image_files_exception
