from fastapi import APIRouter, Depends, HTTPException
from config.logging_config import setup_logging
from databases.database_tools import create_album, get_album, add_photos_to_album, delete_albums
from auth.auth import get_current_user, User
from schemas.albums_schema import CreateAlbumData, AddPhotosToAlbumData, DeleteAlbumsData

router = APIRouter()
logger = setup_logging(__name__)


@router.post("/create-album")
async def create_album_api(data: CreateAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/create-album - Endpoint accessed by user: {current_user['username']}")

    album_name = data.album_name
    parent_id = data.parent_id
    image_ids = data.image_ids

    new_album_id = await create_album(album_name, parent_id)
    if not new_album_id:
        logger.error("/create-album - Failed to create new album")
        raise HTTPException(status_code=500, detail="Failed to create new album")

    logger.info(f"/create-album - Successfully created album: {str(new_album_id)}")

    if image_ids:
        success = await add_photos_to_album(image_ids, new_album_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add images to the new album")

        logger.info(f"/create-album - Successfully added images to new album: {str(new_album_id)}")

    return {"message": "Album created successfully", "album_id": str(new_album_id)}


@router.post("/add-images-to-album")
async def add_images_to_album_api(data: AddPhotosToAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-images-to-album - Endpoint accessed by user: {current_user['username']}")

    album_id = data.album_id
    image_ids = data.image_ids

    if not image_ids:
        logger.warning("/add-images-to-album - No image IDs provided")
        raise HTTPException(status_code=400, detail="No image IDs provided")

    album = await get_album(album_id)
    if not album:
        logger.warning("/add-images-to-album - Album not found")
        raise HTTPException(status_code=404, detail="Album not found")

    success = await add_photos_to_album(image_ids, album_id)
    if not success:
        logger.error("/add-images-to-album - Failed to add photos to the album")
        raise HTTPException(status_code=500, detail="Failed to add photos to the album")

    logger.info(f"/add-images-to-album - Successfully added images to album: {str(album_id)}")
    return {"message": "Images added to album successfully"}


@router.delete("/delete-albums")
async def delete_albums_api(data: DeleteAlbumsData, current_user: User = Depends(get_current_user)):
    logger.info(f"/delete-albums  - Endpoint accessed by user: {current_user['username']}")

    album_ids = data.album_ids

    for album_id in album_ids:
        album = await get_album(album_id)
        if not album:
            logger.warning(f"/delete-albums - Album not found: {album_id}")
            raise HTTPException(status_code=404, detail="Album not found")

    success = await delete_albums(album_ids)
    if not success:
        logger.error(f"/delete-albums - Failed to delete albums: {album_ids}")
        raise HTTPException(status_code=500, detail="Failed to delete albums")

    logger.info(f"/delete-albums - Successfully deleted albums: {album_ids}")

    return {"message": "Albums deleted successfully"}
