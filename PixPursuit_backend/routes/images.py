from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form
from utils.image_similarity import find_similar_images
from databases.database_tools import delete_images, relocate_to_album
from authentication.auth import get_current_user
from data_extraction.image_processing import process_and_save_images
from schemas.images_schema import DeleteImagesData, RelocateImagesData, SimilarImagesData, ScrapeImagesData
from utils.image_scraper import scrape_and_save_images
from utils.function_utils import is_allowed_url
from schemas.auth_schema import User
from utils.exceptions import process_and_save_images_exception, delete_images_exception, relocate_images_exception, \
    find_similar_images_exception, invalid_limit_exception, scrape_and_save_images_exception, invalid_url_exception, \
    no_images_found_exception

router = APIRouter()


@router.post("/process-images")
async def process_images_api(images: List[UploadFile] = File(...), album_id: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    if not images:
        raise no_images_found_exception

    inserted_ids = await process_and_save_images(images, current_user.username, album_id)
    if not inserted_ids:
        raise process_and_save_images_exception

    return {"message": "Images saved successfully", "inserted_ids": inserted_ids}


@router.delete("/delete-images")
async def delete_images_api(data: DeleteImagesData, current_user: User = Depends(get_current_user)):
    success = await delete_images(data.image_ids)
    if not success:
        raise delete_images_exception

    return {"message": "Images deleted successfully"}


@router.post("/relocate-images")
async def relocate_images_api(data: RelocateImagesData, current_user: User = Depends(get_current_user)):
    success = await relocate_to_album(data.prev_album_id, data.new_album_id, data.image_ids)
    if not success:
        raise relocate_images_exception

    return {"message": "Images relocated successfully"}


@router.post("/find-similar-images")
async def find_similar_images_api(data: SimilarImagesData):
    if data.limit < 1:
        raise invalid_limit_exception

    similar_images = await find_similar_images(data.image_id, data.limit)
    if not similar_images:
        raise find_similar_images_exception

    return {"similar_images": similar_images}


@router.post("/scrape-images")
async def scrape_images_api(data: ScrapeImagesData, current_user: User = Depends(get_current_user)):
    if not is_allowed_url(data.url):
        raise invalid_url_exception

    inserted_ids, album_id = await scrape_and_save_images(data.url, current_user.username, data.album_id)
    if not inserted_ids:
        raise scrape_and_save_images_exception

    return {"message": "Images scraped successfully", "inserted_ids": inserted_ids, "album_id": str(album_id)}
