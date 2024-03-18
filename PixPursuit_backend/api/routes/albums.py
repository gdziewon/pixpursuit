from fastapi import APIRouter, Depends, Form, UploadFile, File
from typing import Optional
from data.databases.database_tools import create_album, add_photos_to_album, delete_albums, rename_album
from services.authentication.auth import get_current_user
from api.schemas.albums_schema import CreateAlbumData, AddPhotosToAlbumData, DeleteAlbumsData, RenameAlbumData, SharepointUploadData
from services.images_zip import ZipProcessor
from api.schemas.auth_schema import User
from utils.exceptions import create_album_exception, add_images_to_album_exception, delete_album_exception,\
    rename_album_exception, upload_zip_exception
from services.sharepoint_client import initiate_album_processing

router = APIRouter()


@router.post("/create-album")
async def create_album_api(data: CreateAlbumData, current_user: User = Depends(get_current_user)):
    new_album_id = await create_album(data.album_name, data.parent_id)
    if not new_album_id:
        raise create_album_exception

    if data.image_ids:
        success = await add_photos_to_album(data.image_ids, new_album_id)
        if not success:
            raise create_album_exception

    return {"message": "Album created successfully", "album_id": str(new_album_id)}


@router.post("/add-images-to-album")
async def add_images_to_album_api(data: AddPhotosToAlbumData, current_user: User = Depends(get_current_user)):
    success = await add_photos_to_album(data.image_ids, data.album_id)
    if not success:
        raise add_images_to_album_exception

    return {"message": "Images added to album successfully"}


@router.delete("/delete-albums")
async def delete_albums_api(data: DeleteAlbumsData, current_user: User = Depends(get_current_user)):
    success = await delete_albums(data.album_ids)
    if not success:
        raise delete_album_exception

    return {"message": "Albums deleted successfully"}


@router.post("/upload-zip")
async def upload_zip_api(file: UploadFile = File(...), parent_id: Optional[str] = Form(None), size: Optional[tuple[int, int]] = Form(None), current_user: User = Depends(get_current_user)):
    zip_processor = ZipProcessor(size)
    album_id = await zip_processor.upload_zip(file, parent_id, current_user.username)
    if not album_id:
        raise upload_zip_exception

    return {"message": "Zip file processed successfully", 'album_id': str(album_id)}


@router.put("/rename-album")
async def rename_album_api(data: RenameAlbumData, current_user: User = Depends(get_current_user)):
    success = await rename_album(data.new_name, data.album_id)
    if not success:
        raise rename_album_exception

    return {"message": "Album renamed successfully"}


@router.post("/sharepoint-upload")
async def sharepoint_upload_api(data: SharepointUploadData, current_user: User = Depends(get_current_user)):
    initiate_album_processing.delay(data.sharepoint_url, data.sharepoint_username, data.sharepoint_password, current_user.username, data.parent_id, data.size)
    return {"message": "Image upload initiated successfully"}
