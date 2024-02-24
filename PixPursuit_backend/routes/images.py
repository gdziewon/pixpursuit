from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from config.logging_config import setup_logging
from utils.image_similarity import find_similar_images
from databases.database_tools import get_album, delete_images, relocate_to_album
from authentication.auth import get_current_user
from data_extraction.image_processing import process_and_save_images
from schemas.images_schema import DeleteImagesData, RelocateImagesData, SimilarImagesData, ScrapeImagesData
from utils.image_scraper import scrape_and_save_images
from utils.function_utils import is_allowed_url
from schemas.auth_schema import User

router = APIRouter()
logger = setup_logging(__name__)


@router.post("/process-images")
async def process_images_api(images: List[UploadFile] = File(...), album_id: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")

    inserted_ids = await process_and_save_images(images, current_user.username, album_id)

    if not inserted_ids:
        raise HTTPException(status_code=500, detail="Failed to process and save images")

    return {"message": "Images saved successfully", "inserted_ids": inserted_ids}


@router.delete("/delete-images")
async def delete_images_api(data: DeleteImagesData, current_user: User = Depends(get_current_user)):
    if not data.image_ids:
        raise HTTPException(status_code=400, detail="No image IDs provided")

    success = await delete_images(data.image_ids)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete images")

    return {"message": "Images deleted successfully"}


@router.post("/relocate-images")
async def relocate_images_api(data: RelocateImagesData, current_user: User = Depends(get_current_user)):
    if not await get_album(data.prev_album_id):
        raise HTTPException(status_code=404, detail="Album not found")

    success = await relocate_to_album(data.prev_album_id, data.new_album_id, data.image_ids)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to relocate images")

    return {"message": "Images relocated successfully"}


@router.post("/find-similar-images")
async def find_similar_images_api(data: SimilarImagesData, current_user: User = Depends(get_current_user)):
    if not data.image_id or data.limit < 1:
        raise HTTPException(status_code=400, detail="Invalid request parameters")

    similar_images = await find_similar_images(data.image_id, data.limit)
    return {"similar_images": similar_images}


@router.post("/scrape-images")
async def scrape_images_api(data: ScrapeImagesData, current_user: User = Depends(get_current_user)):
    if not is_allowed_url(data.url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    inserted_ids, album_id = await scrape_and_save_images(data.url, current_user.username, data.album_id)
    if not inserted_ids:
        raise HTTPException(status_code=500, detail="Failed to scrape and save images")

    return {"message": "Images scraped successfully", "inserted_ids": inserted_ids, "album_id": str(album_id)}

