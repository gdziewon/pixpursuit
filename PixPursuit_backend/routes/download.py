import httpx
from fastapi import APIRouter
from utils.images_zip import ZipProcessor
from fastapi.responses import StreamingResponse
from schemas.download_schema import ZipData
from utils.exceptions import no_image_and_album_ids_exception

router = APIRouter()
ZipProcessor = ZipProcessor()


@router.get("/download-image/")
async def download_image(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

        async def iterfile():
            async for chunk in response.aiter_bytes():
                yield chunk

        return StreamingResponse(iterfile(), media_type=response.headers['Content-Type'])


@router.post("/download-zip")
async def download_zip(data: ZipData):
    if not data.album_ids and not data.image_ids:
        raise no_image_and_album_ids_exception

    zip_buffer = await ZipProcessor.generate_zip_file(data.album_ids, data.image_ids)

    def iterfile():
        while True:
            chunk = zip_buffer.read(4096)
            if not chunk:
                break
            yield chunk

    return StreamingResponse(iterfile(), media_type="application/zip")
