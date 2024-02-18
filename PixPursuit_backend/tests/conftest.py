import pytest
from httpx import AsyncClient
import sys
from pathlib import Path
import asyncio
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import app

TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'testpassword'
TEST_ALBUM_ID = '65cbcec9ef7a4c1d9eb2dab1'
TEST_IMAGE_ID = '65cbced6ef7a4c1d9eb2daba'


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def token(async_client):
    response = await async_client.post("/token", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    return response.json()["access_token"]
