import pytest
from httpx import AsyncClient
from pathlib import Path
from unittest.mock import patch
from tests.conftest import TEST_ALBUM_ID, TEST_IMAGE_ID

test_image_path = Path(__file__).parent / 'test.jpg'


@pytest.mark.asyncio
async def test_process_and_delete_image(async_client: AsyncClient, token: str):
    with patch('data_extraction.face_detection.get_face_embeddings.delay') as mock_get_face_embeddings, \
            patch('data_extraction.object_detection.detect_objects.delay') as mock_detect_objects, \
            patch('data_extraction.feature_extraction.extract_features.delay') as mock_extract_features, \
            patch('tag_prediction.tag_prediction_tools.predict_and_update_tags.delay') as mock_predict_and_update_tags:

        files = {'images': (test_image_path.name, test_image_path.open('rb'), 'image/jpeg')}
        data = {'album_id': TEST_ALBUM_ID}
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.post("/process-images", files=files, data=data, headers=headers)
        assert response.status_code == 200
        assert "inserted_ids" in response.json()

        mock_get_face_embeddings.assert_called_once()
        mock_detect_objects.assert_called_once()
        mock_extract_features.assert_called_once()
        mock_predict_and_update_tags.assert_called_once_with(response.json()["inserted_ids"])

        image_ids = response.json()["inserted_ids"]
        delete_response = await async_client.request(
            method="DELETE",
            url="/delete-images",
            json={"image_ids": image_ids},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Images deleted successfully"


@pytest.mark.asyncio
async def test_find_similar_images(async_client: AsyncClient, token: str):
    data = {"image_id": TEST_IMAGE_ID, "limit": 5}
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/find-similar-images", json=data, headers=headers)

    assert response.status_code == 200
    assert "similar_images" in response.json()


@pytest.mark.asyncio
async def test_scrape_images(async_client: AsyncClient, token: str):
    data = {"url": "http://www.galeria.pk.edu.pl/index.php?album=1953-podpisanie-umowy-z-pkp-intercity", "album_id": TEST_ALBUM_ID}
    headers = {"Authorization": f"Bearer {token}"}
    expected_calls = 5
    with patch('data_extraction.face_detection.get_face_embeddings.delay') as mock_get_face_embeddings, \
            patch('data_extraction.object_detection.detect_objects.delay') as mock_detect_objects, \
            patch('data_extraction.feature_extraction.extract_features.delay') as mock_extract_features, \
            patch('tag_prediction.tag_prediction_tools.predict_and_update_tags.delay') as mock_predict_and_update_tags:
        response = await async_client.post("/scrape-images", json=data, headers=headers)

        assert response.status_code == 200
        assert "inserted_ids" in response.json()

        assert mock_get_face_embeddings.call_count == expected_calls
        assert mock_detect_objects.call_count == expected_calls
        assert mock_extract_features.call_count == expected_calls

        mock_predict_and_update_tags.assert_called_once_with(response.json()["inserted_ids"])
