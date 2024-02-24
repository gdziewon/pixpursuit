import httpx
from fastapi import APIRouter, HTTPException, BackgroundTasks
from config.logging_config import setup_logging
from utils.images_zip import generate_zip_file
from fastapi.responses import StreamingResponse, FileResponse
from schemas.download_schema import ZipData
from utils.dirs import get_tmp_dir_path
import os
from urllib.parse import unquote, urlparse

router = APIRouter()
logger = setup_logging(__name__)


@router.get("/download-image/")
async def download_image(url: str, background_tasks: BackgroundTasks):
    decoded_url = unquote(url)

    parsed_url = urlparse(decoded_url)
    path = parsed_url.path
    filename = path.split('/')[-1]

    async with httpx.AsyncClient() as client:
        response = await client.get(decoded_url, follow_redirects=True)
        response.raise_for_status()

        temp_path = f"{get_tmp_dir_path()}/{filename}"
        with open(temp_path, "wb") as f:
            f.write(response.content)

        def cleanup_file(path: str):
            if os.path.exists(path):
                os.remove(path)

        background_tasks.add_task(cleanup_file, temp_path)

        return FileResponse(path=temp_path, media_type='application/octet-stream', filename=filename,
                            headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.post("/download-zip")
async def download_zip(data: ZipData):
    if not data.album_ids and not data.image_ids:
        raise HTTPException(status_code=400, detail="No album IDs or image IDs provided")

    zip_buffer = await generate_zip_file(data.album_ids, data.image_ids)

    def iterfile():
        while True:
            chunk = zip_buffer.read(4096)
            if not chunk:
                break
            yield chunk

    return StreamingResponse(iterfile(), media_type="application/zip")
