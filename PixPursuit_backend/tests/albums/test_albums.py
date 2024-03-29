import asyncio

import pytest
from httpx import AsyncClient
from pathlib import Path
from tests.conftest import TEST_ALBUM_ID
from uuid import uuid4
from unittest.mock import patch

test_zip_path = Path(__file__).parent / 'test.zip'


@pytest.mark.asyncio
async def test_create_and_delete_album(async_client: AsyncClient, token: str, parent_id=None):
    create_headers = {"Authorization": f"Bearer {token}"}
    unique_album_name = f"Test Album for Deletion {uuid4()}"
    create_data = {
        "album_name": unique_album_name,
        "parent_id": parent_id,
        "image_ids": []
    }
    create_response = await async_client.post("/create-album", headers=create_headers, json=create_data)
    assert create_response.status_code == 200
    assert create_response.json()["message"] == "Album created successfully"
    created_album_id = create_response.json()["album_id"]

    delete_headers = {"Authorization": f"Bearer {token}"}
    delete_response = await async_client.request(
        method="DELETE",
        url="/delete-albums",
        headers=delete_headers,
        json={"album_ids": [created_album_id]}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Albums deleted successfully"


@pytest.mark.asyncio
async def test_create_and_delete_album_no_parent(async_client: AsyncClient, token: str):
    await test_create_and_delete_album(async_client, token)


@pytest.mark.asyncio
async def test_create_and_delete_album_with_parent(async_client: AsyncClient, token: str):
    await test_create_and_delete_album(async_client, token, TEST_ALBUM_ID)


@pytest.mark.asyncio
async def test_delete_album_invalid_id(async_client: AsyncClient, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.request(
        method="DELETE",
        url="/delete-albums",
        headers=headers,
        json={"album_ids": ["invalid_id"]}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Album not found: invalid_id"


@pytest.mark.asyncio
async def test_upload_zip(async_client: AsyncClient, token: str):
    with patch('data_extraction.face_detection.get_face_embeddings.delay') as mock_get_face_embeddings, \
            patch('data_extraction.object_detection.detect_objects.delay') as mock_detect_objects, \
            patch('data_extraction.feature_extraction.extract_features.delay') as mock_extract_features, \
            patch('tag_prediction.tag_prediction_tools.predict_and_update_tags.delay') as mock_predict_and_update_tags, \
            patch('databases.face_operations.delete_faces_associated_with_images.delay') as mock_delete_faces:

        expected_calls = 2
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": (test_zip_path.name, test_zip_path.open("rb"), "application/zip")}
        data = {"parent_id": TEST_ALBUM_ID}
        response = await async_client.post("/upload-zip", headers=headers, files=files, data=data)
        assert response.status_code == 200
        assert "Zip file processed successfully" in response.json()["message"]

        await asyncio.sleep(1)

        album_id = response.json()["album_id"]
        delete_response = await async_client.request(
            method="DELETE",
            url="/delete-albums",
            headers=headers,
            json={"album_ids": [album_id]}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Albums deleted successfully"

        assert mock_get_face_embeddings.call_count == expected_calls
        assert mock_detect_objects.call_count == expected_calls
        assert mock_extract_features.call_count == expected_calls
        assert mock_predict_and_update_tags.call_count == expected_calls
        assert mock_delete_faces.call_count == expected_calls


@pytest.mark.asyncio
async def test_rename_album(async_client: AsyncClient, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    new_name = f"Test Album {uuid4()}"
    data = {
        "album_id": TEST_ALBUM_ID,
        "new_name": new_name
    }
    response = await async_client.put("/rename-album", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Album renamed successfully"


@pytest.mark.asyncio
async def test_rename_album_invalid_id(async_client: AsyncClient, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    new_name = f"Test Album {uuid4()}"
    data = {
        "album_id": "invalid_id",
        "new_name": new_name
    }
    response = await async_client.put("/rename-album", headers=headers, json=data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Album not found"
