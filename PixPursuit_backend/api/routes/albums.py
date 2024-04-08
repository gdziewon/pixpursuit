"""
api/routes/albums.py

Contains routes for album management, such as creating, renaming, deleting albums, and
adding or removing images from albums.
"""

from fastapi import APIRouter, Depends, Form, UploadFile, File
from typing import Optional
from data.databases.mongodb.async_db.database_tools import create_album, add_photos_to_album, delete_albums, rename_album
from services.authentication.auth import get_current_user
from api.schemas.albums_schema import CreateAlbumData, AddPhotosToAlbumData, DeleteAlbumsData, RenameAlbumData, \
    SharepointUploadData
from services.images_zip import ZipProcessor
from api.schemas.auth_schema import User
from utils.exceptions import create_album_exception, add_images_to_album_exception, delete_album_exception, \
    rename_album_exception, upload_zip_exception
from services.sharepoint.sharepoint_client import initiate_album_processing

router = APIRouter()


@router.post("/create-album")
async def create_album_api(data: CreateAlbumData, current_user: User = Depends(get_current_user)):
    """
    Create a new album.

    This endpoint creates a new album with the specified name and parent ID,
    and optionally adds photos to the album if image IDs are provided.

    :param data: The data needed to create an album, containing the album name, parent ID, and optional image IDs.
    :type data: CreateAlbumData
    :param current_user: The current user creating the album, obtained from dependency injection.
    :type current_user: User
    :return: A dictionary with a success message and the new album ID.
    :rtype: dict
    """
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
    """
    Add images to an album.

    This endpoint adds the specified images to the album identified by the album ID.

    :param data: The data needed to add images to an album, containing image IDs and the album ID.
    :type data: AddPhotosToAlbumData
    :param current_user: The current user performing the operation, obtained from dependency injection.
    :type current_user: User
    :return: A message indicating successful addition of images to the album.
    :rtype: dict
    """
    success = await add_photos_to_album(data.image_ids, data.album_id)
    if not success:
        raise add_images_to_album_exception

    return {"message": "Images added to album successfully"}


@router.delete("/delete-albums")
async def delete_albums_api(data: DeleteAlbumsData, current_user: User = Depends(get_current_user)):
    """
    Delete albums.

    This endpoint deletes albums identified by the given album IDs.

    :param data: The data containing the IDs of albums to be deleted.
    :type data: DeleteAlbumsData
    :param current_user: The current user performing the delete operation, obtained from dependency injection.
    :type current_user: User
    :return: A message indicating successful deletion of albums.
    :rtype: dict
    """
    success = await delete_albums(data.album_ids)
    if not success:
        raise delete_album_exception

    return {"message": "Albums deleted successfully"}


@router.post("/upload-zip")
async def upload_zip_api(file: UploadFile = File(...), parent_id: Optional[str] = Form(None),
                         size: Optional[tuple[int, int]] = Form(None), current_user: User = Depends(get_current_user)):
    """
    Process and upload a zip file containing images to an album.

    This endpoint handles the uploading and processing of a zip file. It creates a new album
    and adds the extracted images from the zip file to this album.

    :param file: The zip file containing images to be processed and uploaded.
    :type file: UploadFile
    :param parent_id: The parent ID for the new album created from the zip file.
    :type parent_id: Optional[str]
    :param size: The dimensions to which the images should be resized (width, height).
    :type size: Optional[tuple[int, int]]
    :param current_user: The current user performing the operation, obtained from dependency injection.
    :type current_user: User
    :return: A message indicating successful processing of the zip file and the ID of the created album.
    :rtype: dict
    """
    zip_processor = ZipProcessor(size)
    album_id = await zip_processor.upload_zip(file, parent_id, current_user.username)
    if not album_id:
        raise upload_zip_exception

    return {"message": "Zip file processed successfully", 'album_id': str(album_id)}


@router.put("/rename-album")
async def rename_album_api(data: RenameAlbumData, current_user: User = Depends(get_current_user)):
    """
    Rename an album.

    This endpoint renames an existing album to a new name specified in the request.

    :param data: The data containing the new name for the album and the album's ID.
    :type data: RenameAlbumData
    :param current_user: The current user performing the operation, obtained from dependency injection.
    :type current_user: User
    :return: A message indicating the successful renaming of the album.
    :rtype: dict
    """
    success = await rename_album(data.new_name, data.album_id)
    if not success:
        raise rename_album_exception

    return {"message": "Album renamed successfully"}


@router.post("/sharepoint-upload")
async def sharepoint_upload_api(data: SharepointUploadData, current_user: User = Depends(get_current_user)):
    """
    Initiate the upload of images to a SharePoint site.

    This endpoint starts the process of uploading images to a specified SharePoint URL.
    The actual uploading process is handled asynchronously.

    :param data: The data needed for the SharePoint upload, including the SharePoint URL,
                 credentials, and other relevant information.
    :type data: SharepointUploadData
    :param current_user: The current user performing the operation, obtained from dependency injection.
    :type current_user: User
    :return: A message indicating that the image upload process has been initiated.
    :rtype: dict
    """
    initiate_album_processing.delay(data.sharepoint_url, data.sharepoint_username, data.sharepoint_password,
                                    current_user.username, data.parent_id, data.size)
    return {"message": "Image upload initiated successfully"}
