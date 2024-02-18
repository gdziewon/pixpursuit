import pytest
from tests.conftest import TEST_USERNAME, TEST_PASSWORD


@pytest.mark.asyncio
async def test_token_endpoint(async_client):
    response = await async_client.post("/token", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert "access_token" in response.json()
