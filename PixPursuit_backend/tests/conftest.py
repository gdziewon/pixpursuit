import pytest
from httpx import AsyncClient
import sys
from pathlib import Path
import dotenv
from app import app
import os
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
dotenv.load_dotenv()
TEST_USERNAME = os.getenv("TEST_USERNAME")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
TEST_ALBUM_ID = os.getenv("TEST_ALBUM_ID")
TEST_IMAGE_ID = os.getenv("TEST_IMAGE_ID")


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
