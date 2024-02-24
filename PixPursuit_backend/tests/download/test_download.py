from unittest.mock import patch, MagicMock
import pytest
from io import BytesIO
from tests.conftest import TEST_ALBUM_ID, TEST_IMAGE_ID
from httpx import Response, AsyncClient, Request, URL, HTTPStatusError


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_download_image_success(mock_get, async_client):
    async def mock_get_async(*args, **kwargs):
        return Response(200, content=b'image_data', headers={'Content-Type': 'image/jpeg'})

    mock_get.side_effect = mock_get_async

    url = "https://pixpursuit.ams3.digitaloceanspaces.com/pixpursuit/20240213211931_c0d44a.jpeg"
    response = await async_client.get(f"/download-image/?url={url}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    content = await response.aread()
    assert content == b'image_data'


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_download_image_invalid_url(mock_get, async_client: AsyncClient):
    mock_request = Request(method="GET", url=URL("http://example.com/invalid_image.jpg"))

    mock_response = MagicMock(status_code=404)
    mock_get.side_effect = HTTPStatusError(message="Not Found", request=mock_request, response=mock_response)

    url = "http://example.com/invalid_image.jpg"
    try:
        response = await async_client.get(f"/download-image/?url={url}")
    except HTTPStatusError as e:
        assert str(e) == "Not Found"
        return

    assert False, "Expected an HTTPStatusError"


@pytest.mark.asyncio
@patch("databases.image_to_space.space_client.get_object")
@patch("databases.database_tools.get_album")
@patch("databases.database_tools.get_image_document")
async def test_download_zip_success(mock_get_image_document, mock_get_album, mock_space_client_get_object,
                                    async_client: AsyncClient):
    mock_get_album.return_value = {"album_id": TEST_ALBUM_ID, "name": "Album 1"}
    mock_get_image_document.return_value = {"image_id": TEST_IMAGE_ID, "filename": "image1.jpg"}
    mock_space_client_get_object.return_value = {"Body": BytesIO(b"image data")}

    data = {"album_ids": [TEST_ALBUM_ID], "image_ids": [TEST_IMAGE_ID]}
    response = await async_client.post("/download-zip", json=data)

    assert response.status_code == 200
    assert "application/zip" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_download_zip_invalid_ids(async_client: AsyncClient):
    data = {"album_ids": ["nonexistent_album"], "image_ids": ["nonexistent_image"]}
    response = await async_client.post("/download-zip", json=data)

    assert response.status_code == 500
