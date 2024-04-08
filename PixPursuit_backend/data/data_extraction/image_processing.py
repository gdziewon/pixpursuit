"""
data/data_extraction/image_processing.py

Manages the complete workflow of image processing, including reading, transforming,
extracting features, detecting faces, and saving the processed data to the database.
It orchestrates the calls to various services and utilities to handle images uploaded
by users.
"""

from bson import ObjectId
from data.databases.space_manager import SpaceManager
from data.data_extraction.metadata_extraction import get_exif_data
from data.data_extraction.face_detection import get_face_embeddings
from data.data_extraction.feature_extraction import extract_features
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile
from io import BytesIO
from config.logging_config import setup_logging
from data.databases.mongodb.async_db.database_tools import save_image_to_database
from data.databases.mongodb.sync_db.celery_database_tools import add_field_to_image
from services.tag_prediction.tag_prediction_tools import predict_and_update_tags
import asyncio
from utils.function_utils import image_to_byte_array
from celery import shared_task
from utils.dirs import cleanup_dir
import os
from utils.constants import EXTRACT_DATA_TASK, MAIN_QUEUE

logger = setup_logging(__name__)

SpaceManager = SpaceManager()


async def read_image(file: UploadFile, size: tuple[int, int] = None) -> Image:
    """
    Asynchronously reads an image from an uploaded file and optionally resizes it.

    :param file: The uploaded file to read the image from.
    :param size: Optional tuple specifying the size to which the image should be resized.
    :return: The PIL Image object, or None if an error occurs during reading or resizing.
    """
    contents = await file.read()
    try:
        image = Image.open(BytesIO(contents))
        if size:
            image.thumbnail(size, Image.LANCZOS)
        return image
    except UnidentifiedImageError as e:
        logger.error(f"Unsupported image format or corrupt image file: {e}")
        return None


async def process_image(file: UploadFile, size: tuple[int, int] = None) -> tuple[str, str, str, dict] or None:
    """
    Processes an uploaded image file by reading, saving to cloud storage, and extracting EXIF data.

    :param file: The uploaded file to process.
    :param size: Optional tuple specifying the size to which the image should be resized.
    :return: A tuple containing the image URL, thumbnail URL, filename, and EXIF data, or None if an error occurs.
    """
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
    """
    Processes and saves multiple images to the database.

    :param images: A list of uploaded image files to process.
    :param user: The user uploading the images.
    :param album_id: The album ID where the images will be saved.
    :param size: Optional dimensions to resize the images to.
    :return: True if all images are processed and saved successfully, otherwise False.
    """
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
    """
    Processes a single image, saves it to the database, and returns its database ID.

    :param image: The image file to process.
    :param user: The user uploading the image.
    :param album_id: The album ID where the image will be saved.
    :param size: Optional dimensions to resize the image to.
    :return: The ID of the saved image in the database, or None if an error occurs.
    """
    try:
        result = await process_image(image, size)
        inserted_id = await save_image_to_database(result, user, album_id)
        return inserted_id
    except Exception as e:
        logger.error(f"Failed to process and save image: {e}")
        return None


def make_batch(iterable: list, n: int = 1):
    """
    Splits an iterable into batches of a specified size.

    :param iterable: The iterable to split into batches.
    :param n: The number of elements each batch should contain.
    :return: A generator yielding batches from the iterable.
    """
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]


async def process_images_from_directory(directory: str, user: str, album_id: ObjectId or str, size: [int, int] = None, batch_size: int = 30) -> bool:
    """
    Processes and saves images from a specified directory to the database.

    :param directory: The directory containing the images to process.
    :param user: The user under which the images are being processed.
    :param album_id: The album ID where the images will be saved.
    :param size: Optional dimensions to resize the images to.
    :param batch_size: The number of images to process in a batch.
    :return: True if all images are processed and saved successfully, otherwise False.
    """
    try:
        image_files = os.listdir(directory)
        batches = list(make_batch(image_files, batch_size))

        for batch in batches:
            images = [UploadFile(filename=os.path.join(directory, image_file),
                                 file=BytesIO(open(os.path.join(directory, image_file), 'rb').read()))
                      for image_file in batch]
            await process_and_save_images(images, user, album_id, size)

        return True
    except Exception as e:
        logger.error(f"Failed to process images from directory: {e}")
        return False
    finally:
        cleanup_dir(directory)  # Clean up the directory after processing


@shared_task(name=EXTRACT_DATA_TASK, queue=MAIN_QUEUE)
def extract_data(image_byte_arr: bytes, filename: str) -> None:
    """
        Extracts various types of data from an image and saves it to the database.

        :param image_byte_arr: Byte array of the image to extract data from.
        :param filename: The filename of the image.
    """
    try:
        image = Image.open(BytesIO(image_byte_arr))
        image = image.convert("RGB")  # Convert image to RGB format
        embeddings_list, boxes_list, user_faces_list = get_face_embeddings(image)  # Extract face embeddings
        features_list = extract_features(image)  # Extract image features

        for name_of_data, data in zip(['embeddings', 'embeddings_box', 'user_faces', 'backlog_faces', 'features'],
                                      [embeddings_list, boxes_list, user_faces_list, user_faces_list, features_list]):
            add_field_to_image(name_of_data, data, filename)
    except RuntimeError as e:
        logger.error(f"Runtime error occurred: {e}")
        return

