import pytest
from tests.conftest import TEST_USERNAME, TEST_PASSWORD, TEST_EMAIL


@pytest.mark.asyncio
async def test_token_endpoint(async_client):
    response = await async_client.post("/token", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_token_endpoint_email(async_client):
    response = await async_client.post("/token", data={"username": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_token_endpoint_invalid_credentials(async_client):
    response = await async_client.post("/token", data={"username": "invalid", "password": "invalid"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}