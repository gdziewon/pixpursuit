from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.logging_config import setup_logging

from auth.auth import get_current_user, User
from databases.sharepoint_client import SharePointClient

router = APIRouter()
logger = setup_logging(__name__)
sharepoint_client = SharePointClient()


class CopyAlbumToSharePointData(BaseModel):
    album_id: str
    folder_name: str
    sharepoint_url: str
    access_token: str


@router.post("/copy-album-to-sharepoint")
async def copy_album_to_sharepoint(data: CopyAlbumToSharePointData, current_user: User = Depends(get_current_user)):
    logger.info(f"/copy-album-to-sharepoint - Endpoint accessed by user: {current_user['username']}")
    success = await sharepoint_client.copy_album_to_sharepoint(data.album_id, data.folder_name, data.sharepoint_url, data.access_token)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to copy album to SharePoint")
    return {"message": "Album copied to SharePoint successfully"}


class CopyAlbumFromSharePointData(BaseModel):
    folder_name: str
    sharepoint_url: str
    access_token: str


@router.post("/copy-album-from-sharepoint")
async def copy_album_from_sharepoint(data: CopyAlbumFromSharePointData, current_user: User = Depends(get_current_user)):
    logger.info(f"/copy-album-from-sharepoint - Endpoint accessed by user: {current_user['username']}")
    success = await sharepoint_client.copy_album_from_sharepoint(data.folder_name, data.sharepoint_url, data.access_token)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to copy album from SharePoint")
    return {"message": "Album copied from SharePoint successfully"}


class CopyImagesToSharePointData(BaseModel):
    image_ids: List[str]
    folder_name: str
    sharepoint_url: str
    access_token: str


@router.post("/copy-images-to-sharepoint")
async def copy_images_to_sharepoint(data: CopyImagesToSharePointData, current_user: User = Depends(get_current_user)):
    logger.info(f"/copy-images-to-sharepoint - Endpoint accessed by user: {current_user['username']}")
    await sharepoint_client.copy_images_to_sharepoint(data.image_ids, data.folder_name, data.sharepoint_url, data.access_token)
    return {"message": "Images copied to SharePoint successfully"}


class CopyImagesFromSharePointData(BaseModel):
    items: List[Tuple[str, str]]
    folder_name: str
    sharepoint_url: str
    access_token: str


@router.post("/copy-images-from-sharepoint")
async def copy_images_from_sharepoint(data: CopyImagesFromSharePointData, current_user: User = Depends(get_current_user)):
    logger.info(f"/copy-images-from-sharepoint - Endpoint accessed by user: {current_user['username']}")
    inserted_ids = await sharepoint_client.copy_images_from_sharepoint(data.items, data.folder_name, data.sharepoint_url, data.access_token)
    return {"message": "Images copied from SharePoint successfully", "inserted_ids": inserted_ids}
