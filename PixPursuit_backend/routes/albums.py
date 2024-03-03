import os
import shutil
from zipfile import ZipFile
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from typing import Optional
from databases.database_tools import create_album, add_photos_to_album, delete_albums, rename_album
from authentication.auth import get_current_user
from schemas.albums_schema import CreateAlbumData, AddPhotosToAlbumData, DeleteAlbumsData, RenameAlbumData
from utils.dirs import get_tmp_dir_path
from utils.images_zip import process_folder
from schemas.auth_schema import User

router = APIRouter()


@router.post("/create-album")
async def create_album_api(data: CreateAlbumData, current_user: User = Depends(get_current_user)):
    new_album_id = await create_album(data.album_name, data.parent_id)
    if not new_album_id:
        raise HTTPException(status_code=500, detail="Failed to create new album")

    if data.image_ids:
        success = await add_photos_to_album(data.image_ids, new_album_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add images to the new album")

    return {"message": "Album created successfully", "album_id": str(new_album_id)}


@router.post("/add-images-to-album")
async def add_images_to_album_api(data: AddPhotosToAlbumData, current_user: User = Depends(get_current_user)):
    success = await add_photos_to_album(data.image_ids, data.album_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add photos to the album")

    return {"message": "Images added to album successfully"}


@router.delete("/delete-albums")
async def delete_albums_api(data: DeleteAlbumsData, current_user: User = Depends(get_current_user)):
    success = await delete_albums(data.album_ids)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete albums")

    return {"message": "Albums deleted successfully"}


@router.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...), parent_id: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    tmp_dir = get_tmp_dir_path()
    temp_file = os.path.join(tmp_dir, file.filename)
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with ZipFile(temp_file, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)

    os.remove(temp_file)

    filename_without_extension, _ = os.path.splitext(file.filename)
    album_id = await create_album(filename_without_extension, parent_id)
    await process_folder(tmp_dir, current_user.username, album_id)
    shutil.rmtree(tmp_dir)

    return {"message": "Zip file processed successfully", 'album_id': str(album_id)}


@router.put("/rename-album")
async def rename_album_api(data: RenameAlbumData, current_user: User = Depends(get_current_user)):
    success = await rename_album(data.new_name, data.album_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to rename album")

    return {"message": "Album renamed successfully"}
