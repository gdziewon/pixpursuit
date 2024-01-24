from fastapi import APIRouter, HTTPException
from config.logging_config import setup_logging
from utils.images_to_zip import add_album_to_zip
from databases.database_tools import get_image_document
from fastapi.responses import StreamingResponse
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
import requests
from databases.database_tools import get_album
from databases.image_to_space import space_client
from schemas.download_schema import DownloadData, ZipData

router = APIRouter()
logger = setup_logging(__name__)


@router.get("/download-image/")
async def download_image(data: DownloadData):
    url = data.url
    try:
        response = requests.get(url, stream=True)

        def iterfile():
            for chunk in response.iter_content(chunk_size=1024):
                yield chunk

        return StreamingResponse(iterfile(), media_type=response.headers['Content-Type'])
    except Exception as e:
        logger.info(f"/download-image - Failed to download image {url} - {e}")
        raise HTTPException(status_code=400, detail="Failed to download image")


@router.post("/download-zip")
async def download_zip(data: ZipData):
    album_ids = data.album_ids
    image_ids = data.image_ids
    logger.info(f"Received request to download zip with album_ids: {album_ids} and image_ids: {image_ids}")
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as zipf:
        for album_id in album_ids:
            album = await get_album(album_id)
            if not album:
                raise HTTPException(status_code=404, detail=f"Album {album_id} not found")
            await add_album_to_zip(album, zipf, "")

        for image_id in image_ids:
            image = await get_image_document(image_id)
            if not image:
                raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
            response = space_client.get_object(Bucket='pixpursuit', Key=image['filename'])
            file_content = response['Body'].read()
            zipf.writestr(image['filename'], file_content)

    zip_buffer.seek(0)

    def iterfile():
        yield from zip_buffer

    return StreamingResponse(iterfile(), media_type="application/zip")
