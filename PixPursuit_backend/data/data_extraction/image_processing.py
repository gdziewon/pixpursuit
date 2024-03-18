from bson import ObjectId
from data.databases.space_manager import SpaceManager
from data.data_extraction.metadata_extraction import get_exif_data
from data.data_extraction.face_detection import get_face_embeddings
from data.data_extraction.feature_extraction import extract_features
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile
from io import BytesIO
from config.logging_config import setup_logging
from data.databases.database_tools import save_image_to_database
from data.databases.celery_database_tools import add_something_to_image
from services.tag_prediction.tag_prediction_tools import predict_and_update_tags
import asyncio
from utils.function_utils import image_to_byte_array
from celery import shared_task
from utils.dirs import cleanup_dir
import os

logger = setup_logging(__name__)
SpaceManager = SpaceManager()


async def read_image(file: UploadFile, size: tuple[int, int] = None) -> Image:
    contents = await file.read()
    try:
        image = Image.open(BytesIO(contents))
        if size:
            image.thumbnail(size, Image.LANCZOS)
        return image
    except UnidentifiedImageError as e:
        logger.error(f"Unsupported image format or corrupt image file: {e}")
        return None


@shared_task(name="image_processing.extract_data.main", queue="main_queue")
def extract_data(image_byte_arr: bytes, filename: str) -> None:
    try:
        image = Image.open(BytesIO(image_byte_arr))
        image = image.convert("RGB")
        embeddings_list, boxes_list, user_faces_list = get_face_embeddings(image)
        features_list = extract_features(image)

        for name_of_data, data in zip(['embeddings', 'embeddings_box', 'user_faces', 'backlog_faces', 'features'],
                                      [embeddings_list, boxes_list, user_faces_list, user_faces_list,  features_list]):
            add_something_to_image(name_of_data, data, filename)
    except RuntimeError as e:
        logger.error(f"Runtime error occurred: {e}")
        return


async def process_image(file: UploadFile, size: tuple[int, int] = None) -> tuple[str, str, str, dict] or None:
    try:
        image = await read_image(file, size)

        image_byte_arr = await image_to_byte_array(image)
        image_url, thumbnail_url, filename = await SpaceManager.save_image_to_space(image)
        exif_data = await get_exif_data(image)

        extract_data.delay(image_byte_arr, filename)
    except RuntimeError as e:
        logger.error(f"Runtime error occurred: {e}")
        return None, None, None, None

    return image_url, thumbnail_url, filename, exif_data


async def process_and_save_images(images: list[UploadFile], user: str, album_id: ObjectId or str, size: [int, int] = None) -> bool:
    inserted_ids = []
    tasks = [process_and_save_image(image, user, album_id, size) for image in images]
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
            if result:
                inserted_ids.append(result)
        except Exception as e:
            logger.error(f"Failed to process and save image: {e}")
            continue
    predict_and_update_tags.delay(inserted_ids)
    return True


async def process_and_save_image(image: UploadFile, user: str, album_id: ObjectId or str, size: [int, int] = None) -> str or None:
    try:
        result = await process_image(image, size)
        inserted_id = await save_image_to_database(result, user, album_id)
        return inserted_id
    except Exception as e:
        logger.error(f"Failed to process and save image: {e}")
        return None


def make_batch(iterable: list, n: int = 1):
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]


async def process_images_from_directory(directory: str, user: str, album_id: ObjectId or str, size: [int, int] = None, batch_size: int = 30) -> bool:
    try:
        image_files = os.listdir(directory)
        batches = list(make_batch(image_files, batch_size))

        for batch in batches:
            images = [UploadFile(filename=os.path.join(directory, image_file),
                                 file=BytesIO(open(os.path.join(directory, image_file), 'rb').read())) for image_file in batch]
            await process_and_save_images(images, user, album_id, size)

        return True
    except Exception as e:
        logger.error(f"Failed to process images from directory: {e}")
        return False
    finally:
        cleanup_dir(directory)
