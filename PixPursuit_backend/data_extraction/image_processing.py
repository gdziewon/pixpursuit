from databases.image_to_space import save_image_to_space
from data_extraction.metadata_extraction import get_exif_data_async
from data_extraction.face_detection import get_face_embeddings
from data_extraction.object_detection import detect_objects
from data_extraction.feature_extraction import extract_features
from PIL import Image
from fastapi import UploadFile
from io import BytesIO
from config.logging_config import setup_logging

logger = setup_logging(__name__)


async def image_to_byte_array(image: Image) -> bytes:
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


async def read_image(file: UploadFile) -> Image:
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    return image


async def process_image_async(upload_file: UploadFile):
    try:
        image = await read_image(upload_file)
        image_byte_arr = await image_to_byte_array(image)

        image_url, thumbnail_url, filename = await save_image_to_space(image)
        exif_data = await get_exif_data_async(image)

        get_face_embeddings.delay(image_byte_arr, filename)
        detect_objects.delay(image_byte_arr, filename)
        extract_features.delay(image_byte_arr, filename)
    except RuntimeError as e:
        logger.error(f"Runtime error occurred: {e}")
        return

    return image_url, thumbnail_url, filename, exif_data
