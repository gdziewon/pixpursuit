from io import BytesIO
from databases.image_to_space import space_client
from databases.database_tools import get_album, get_image_document, get_root_id, create_album
import os
import asyncio
from config.logging_config import setup_logging
from utils.function_utils import is_allowed_file
from fastapi import UploadFile
from data_extraction.image_processing import process_and_save_images
from utils.constants import BUCKET_NAME

logger = setup_logging(__name__)


async def add_album_to_zip(album, zipf, path, depth=0, max_depth=5):
    if depth > max_depth:
        logger.warn(f"Maximum album recursion depth reached at album: {album['name']}")
        return

    logger.info(f"Adding album: {album['name']} to zip at path: {path}")
    path = os.path.join(path, album['name'])

    image_tasks = [get_image_document(image_id) for image_id in album['images']]
    sub_album_tasks = [get_album(sub_album_id) for sub_album_id in album['sons']]
    images_and_albums = await asyncio.gather(*image_tasks, *sub_album_tasks, return_exceptions=True)

    for image in images_and_albums[:len(album['images'])]:
        try:
            if image:
                await add_image_to_zip(image, zipf, path)
        except Exception as e:
            logger.error(f"Failed to process image: {image['filename']} in album: {album['name']} - {e}")

    for sub_album in images_and_albums[len(album['images']):]:
        try:
            if sub_album:
                await add_album_to_zip(sub_album, zipf, path, depth=depth + 1, max_depth=max_depth)
        except Exception as e:
            logger.error(f"Failed to process sub-album: {sub_album['name']} in album: {album['name']} - {e}")


async def add_image_to_zip(image, zipf, path):
    try:
        response = space_client.get_object(Bucket=BUCKET_NAME, Key=image['filename'])
        file_content = response['Body'].read()
        zipf.writestr(os.path.join(path, image['filename']), file_content)
    except Exception as e:
        logger.error(f"Failed to add image: {image['filename']} to zip - {e}")


async def process_folder(path, username, parent_id=None):
    if parent_id is None:
        parent_id = await get_root_id()

    image_files = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            logger.info(f"Processing sub-directory: {item_path}")
            album_id = await create_album(item, parent_id)
            logger.info(f"Created album: {album_id}")
            await process_folder(item_path, username, album_id)
        elif os.path.isfile(item_path) and is_allowed_file(item_path):
            logger.info(f"Processing file: {item_path}")
            with open(item_path, 'rb') as file:
                contents = file.read()
            upload_file = UploadFile(filename=item, file=BytesIO(contents))
            image_files.append(upload_file)

    inserted_ids = await process_and_save_images(image_files, username, parent_id)

    return inserted_ids
