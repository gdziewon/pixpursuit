import asyncio

import pytest
from httpx import AsyncClient
from uuid import uuid4
from tests.conftest import TEST_IMAGE_ID
from unittest.mock import patch


@pytest.mark.asyncio
async def test_add_and_remove_user_tag_and_feedback(async_client: AsyncClient, token: str):
    with patch('tag_prediction.tag_prediction_tools.train_model.delay') as mock_train_model:
        headers = {"Authorization": f"Bearer {token}"}
        tag1 = f"Test Tag 1 {uuid4()}"
        tag2 = f"Test Tag 2 {uuid4()}"

        # add tags
        add_tag_data = {
            "inserted_id": TEST_IMAGE_ID,
            "tags": [tag1, tag2]
        }
        response = await async_client.post("/add-user-tag", headers=headers, json=add_tag_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Tags added successfully"

        await asyncio.sleep(1)

        # add feedback
        add_feedback_data = {
            "inserted_id": TEST_IMAGE_ID,
            "tag": tag1,
            "is_positive": True
        }
        response = await async_client.post("/feedback-on-tags", headers=headers, json=add_feedback_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Feedback added successfully"

        await asyncio.sleep(1)

        remove_tag_data = {
            "image_id": TEST_IMAGE_ID,
            "tags": [tag1, tag2]
        }
        response = await async_client.post("/remove-tags", headers=headers, json=remove_tag_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Tags removed successfully"

        assert mock_train_model.call_count == 3


@pytest.mark.asyncio
async def test_add_tags_to_selected(async_client: AsyncClient, token: str):
    with patch('tag_prediction.tag_prediction_tools.train_model.delay') as mock_train_model:
        headers = {"Authorization": f"Bearer {token}"}
        tag1 = f"Test Tag 1 {uuid4()}"
        tag2 = f"Test Tag 2 {uuid4()}"
        data = {
            "image_ids": [TEST_IMAGE_ID],
            "album_ids": [],
            "tags": [tag1, tag2]
        }
        response = await async_client.post("/add-tags-to-selected", headers=headers, json=data)
        assert response.status_code == 200
        assert response.json()["message"] == "Tags added to selected items successfully"

        await asyncio.sleep(1)

        data = {
            "inserted_id": TEST_IMAGE_ID,
            "tags": [tag1, tag2]
        }

        # remove tags
        remove_tag_data = {
            "image_id": TEST_IMAGE_ID,
            "tags": [tag1, tag2]
        }
        response = await async_client.post("/remove-tags", headers=headers, json=remove_tag_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Tags removed successfully"

        assert mock_train_model.call_count == 2


@pytest.mark.asyncio
async def test_add_description(async_client: AsyncClient, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    description = f"Test description {uuid4()}"
    data = {
        "inserted_id": TEST_IMAGE_ID,
        "description": description
    }
    response = await async_client.post("/add-description", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Description added successfully"


@pytest.mark.asyncio
async def test_add_like(async_client: AsyncClient, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    like_data = {
        "inserted_id": TEST_IMAGE_ID,
        "is_positive": True
    }
    response = await async_client.post("/add-like", headers=headers, json=like_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Like added successfully"

    dislike_data = {
        "inserted_id": TEST_IMAGE_ID,
        "is_positive": False
    }
    response = await async_client.post("/add-like", headers=headers, json=dislike_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Like added successfully"


@pytest.mark.asyncio
async def test_add_view(async_client: AsyncClient):
    data = {
        "inserted_id": TEST_IMAGE_ID
    }
    response = await async_client.post("/add-view", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "View added successfully"


# @pytest.mark.asyncio
# async def test_add_user_face(async_client: AsyncClient, token: str):
#     with patch('databases.face_operations.update_names.delay') as mock_update_names:
#         headers = {"Authorization": f"Bearer {token}"}
#         name = f"Person Name {uuid4()}"
#         data = {
#             "inserted_id": TEST_IMAGE_ID,
#             "anonymous_index": 0,
#             "name": name
#         }
#         response = await async_client.post("/add-user-face", headers=headers, json=data)
#         assert response.status_code == 200
#         assert response.json()["message"] == "Name added successfully"
#
#         mock_update_names.assert_called_once()
