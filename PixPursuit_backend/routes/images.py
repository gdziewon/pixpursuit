from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from config.logging_config import setup_logging
from utils.image_similarity import find_similar_images
from databases.database_tools import get_album, delete_images, relocate_to_album
from authentication.auth import get_current_user, User
from data_extraction.image_processing import process_and_save_images
from schemas.images_schema import DeleteImagesData, RelocateImagesData, SimilarImagesData, ScrapeImagesData
from utils.image_scraper import scrape_and_save_images
from utils.function_utils import is_allowed_url

router = APIRouter()
logger = setup_logging(__name__)


@router.post("/process-images")
async def process_images_api(images: List[UploadFile] = File(...), album_id: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    logger.info(f"/process-images - Endpoint accessed by user: {current_user['username']}")

    if not images:
        logger.warning(f"/process-images - No images provided")
        raise HTTPException(status_code=400, detail="No images provided")

    inserted_ids = await process_and_save_images(images, current_user['username'], album_id)

    if not inserted_ids:
        logger.error("/process-images - Failed to process and save images")
        raise HTTPException(status_code=500, detail="Failed to process and save images")

    logger.info(f"/process-images - Successfully processed and saved images: {inserted_ids}")
    return {"message": "Images saved successfully", "inserted_ids": inserted_ids}


@router.delete("/delete-images")
async def delete_images_api(data: DeleteImagesData, current_user: User = Depends(get_current_user)):
    logger.info(f"/delete-images - Endpoint accessed by user: {current_user['username']}")

    image_ids = data.image_ids
    if not image_ids:
        logger.warning("/delete-images - No image IDs provided")
        raise HTTPException(status_code=400, detail="No image IDs provided")

    success = await delete_images(image_ids)
    if not success:
        logger.error("/delete-images - Failed to delete images")
        raise HTTPException(status_code=500, detail="Failed to delete images")

    logger.info(f"/delete-images - Successfully deleted images: {image_ids}")
    return {"message": "Images deleted successfully"}


@router.post("/relocate-images")
async def relocate_images_api(data: RelocateImagesData, current_user: User = Depends(get_current_user)):
    logger.info(f"/relocate-images  - Endpoint accessed by user: {current_user['username']}")

    image_ids = data.image_ids
    prev_album_id = data.prev_album_id
    new_album_id = data.new_album_id

    album = await get_album(prev_album_id)
    if not album:
        logger.warning("/relocate-images - Album not found")
        raise HTTPException(status_code=404, detail="Album not found")

    success = await relocate_to_album(prev_album_id, new_album_id, image_ids,)
    if not success:
        logger.error("/relocate-images - Failed to relocate images")
        raise HTTPException(status_code=500, detail="Failed to relocate images")

    logger.info(f"Successfully relocated images from album: {prev_album_id}")
    return {"message": "Images relocated successfully"}


@router.post("/find-similar-images")
async def find_similar_images_api(data: SimilarImagesData):
    image_id = data.image_id
    limit = data.limit

    try:
        similar_images = await find_similar_images(image_id, limit)
        logger.info(f"/find-similar-images - Successfully found similar images for {image_id}: {similar_images}")
        return {"similar_images": similar_images}
    except Exception as e:
        logger.error(f"/find-similar-images - Error finding similar images for {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Error finding similar images")


@router.post("/scrape-images")
async def scrape_images_api(data: ScrapeImagesData, current_user: User = Depends(get_current_user)):
    logger.info(f"/scrape-images - Endpoint accessed by user: {current_user['username']}")
    url = data.url
    album_id = data.album_id

    if not is_allowed_url(url):
        logger.warning(f"/scrape-images - Invalid URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL")

    inserted_ids = await scrape_and_save_images(url, current_user['username'], album_id)
    if not inserted_ids:
        logger.error("/scrape-images - Failed to scrape and save images")
        raise HTTPException(status_code=500, detail="Failed to scrape and save images")

    logger.info(f"/scrape-images - Successfully scraped and saved images: {inserted_ids}")

    return {"message": "Images scraped successfully", "inserted_ids": inserted_ids}
