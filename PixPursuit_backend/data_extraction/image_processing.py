from databases.image_to_space import save_image_to_space
from data_extraction.metadata_extraction import get_exif_data_async
from data_extraction.face_detection import get_face_embeddings
from data_extraction.object_detection import detect_objects
from data_extraction.feature_extraction import extract_features
from PIL import Image
from fastapi import UploadFile
from io import BytesIO
from config.logging_config import setup_logging
from databases.database_tools import save_image_to_database
from tag_prediction.tag_prediction_tools import predict_and_update_tags
import asyncio

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


async def process_image(file: UploadFile):
    try:
        image = await read_image(file)

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


async def process_and_save_images(images, user, album_id):
    try:
        processed_images = [asyncio.create_task(process_image(image)) for image in images]
        results = await asyncio.gather(*processed_images)
        inserted_ids = []
        for result in results:
            inserted_id = await save_image_to_database(result, user, album_id)
            if inserted_id:
                inserted_ids.append(inserted_id)

        predict_and_update_tags.delay(inserted_ids)
        return inserted_ids
    except Exception as e:
        logger.error(f"Failed to process and save images: {e}")
        return []
