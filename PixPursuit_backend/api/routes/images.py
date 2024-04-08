"""
api/routes/images.py

Defines routes for image-related operations, such as uploading, processing, deleting images,
and performing actions like finding similar images or scraping images from external sources.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form
from services.image_similarity import ImageSimilarity
from data.databases.mongodb.async_db.database_tools import delete_images, relocate_to_album
from services.authentication.auth import get_current_user
from data.data_extraction.image_processing import process_and_save_images
from api.schemas.images_schema import DeleteImagesData, RelocateImagesData, SimilarImagesData, ScrapeImagesData
from services.image_scraper import ImageScraper
from utils.function_utils import is_allowed_url
from api.schemas.auth_schema import User
from utils.exceptions import process_and_save_images_exception, delete_images_exception, relocate_images_exception, \
    find_similar_images_exception, invalid_limit_exception, scrape_and_save_images_exception, invalid_url_exception, \
    no_images_found_exception

router = APIRouter()


@router.post("/process-images")
async def process_images_api(images: List[UploadFile] = File(...), album_id: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    """
    Process and save uploaded images.

    :param images: A list of images to process and save.
    :type images: List[UploadFile]
    :param album_id: The ID of the album where the images should be saved, if any.
    :type album_id: Optional[str]
    :param current_user: The user who is uploading the images.
    :type current_user: User
    :return: A message indicating successful processing and saving of images.
    :rtype: dict
    """
    if not images:
        raise no_images_found_exception

    success = await process_and_save_images(images, current_user.username, album_id)
    if not success:
        raise process_and_save_images_exception

    return {"message": "Images saved successfully"}


@router.delete("/delete-images")
async def delete_images_api(data: DeleteImagesData, current_user: User = Depends(get_current_user)):
    """
    Delete specified images.

    :param data: Data containing the IDs of images to be deleted.
    :type data: DeleteImagesData
    :param current_user: The user requesting the deletion.
    :type current_user: User
    :return: A message indicating successful deletion of images.
    :rtype: dict
    """
    success = await delete_images(data.image_ids)
    if not success:
        raise delete_images_exception

    return {"message": "Images deleted successfully"}


@router.post("/relocate-images")
async def relocate_images_api(data: RelocateImagesData, current_user: User = Depends(get_current_user)):
    """
    Relocate images from one album to another.

    :param data: Data containing the previous and new album IDs, and the image IDs to relocate.
    :type data: RelocateImagesData
    :param current_user: The user performing the relocation.
    :type current_user: User
    :return: A message indicating successful relocation of images.
    :rtype: dict
    """
    success = await relocate_to_album(data.prev_album_id, data.new_album_id, data.image_ids)
    if not success:
        raise relocate_images_exception

    return {"message": "Images relocated successfully"}


@router.post("/find-similar-images")
async def find_similar_images_api(data: SimilarImagesData):
    """
    Find images similar to a given image.

    :param data: Data containing the image ID and the limit on the number of similar images to return.
    :type data: SimilarImagesData
    :return: A list of similar images.
    :rtype: dict
    """
    if data.limit < 1:
        raise invalid_limit_exception

    similarity = ImageSimilarity()
    similar_images = await similarity.find_similar_images(data.image_id, data.limit)
    if not similar_images:
        raise find_similar_images_exception

    return {"similar_images": similar_images}


@router.post("/scrape-images")
async def scrape_images_api(data: ScrapeImagesData, current_user: User = Depends(get_current_user)):
    """
    Scrape images from a specified URL (only for galeria.pk albums) and save them to the album.

    :param data: Data containing the URL to scrape from and the album ID to save the images.
    :type data: ScrapeImagesData
    :param current_user: The user performing the scraping.
    :type current_user: User
    :return: A message indicating successful scraping and saving of images, along with the album ID.
    :rtype: dict
    """
    if not is_allowed_url(data.url):
        raise invalid_url_exception

    scraper = ImageScraper()
    album_id = await scraper.scrape_and_save_images(data.url, current_user.username, data.album_id)
    await scraper.close()
    if not album_id:
        raise scrape_and_save_images_exception

    return {"message": "Images scraped successfully", "album_id": str(album_id)}
