from io import BytesIO
from bs4 import BeautifulSoup
from config.logging_config import setup_logging
import os
from utils.dirs import get_tmp_dir_path
from urllib.parse import urlparse, parse_qs, urljoin
from databases.database_tools import create_album
from fastapi import UploadFile
from data_extraction.image_processing import process_and_save_images
import shutil
import httpx
import asyncio
from utils.constants import BASE_URL
from utils.exceptions import get_images_exception, get_soup_exception, scrape_images_exception, \
    prepare_image_files_exception, clean_up_exception

logger = setup_logging(__name__)


async def get_image_urls(soup: BeautifulSoup) -> list[str]:
    try:
        image_links = soup.find_all('a', attrs={'rel': 'lightbox-album'})
        full_image_urls = [urljoin(BASE_URL, link['href']) for link in image_links]
        return full_image_urls
    except Exception as e:
        logger.error(f"Failed to get image URLs: {e}")
        raise get_images_exception


async def get_soup(url: str) -> BeautifulSoup:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.RequestError as e:
            logger.error(f"Failed to get soup: {e}")
            raise get_soup_exception

    return BeautifulSoup(response.text, 'html.parser')


async def fetch_image(image_url: str, save_dir: str, client: httpx.AsyncClient) -> None:
    try:
        parsed_url = urlparse(image_url)
        query_params = parse_qs(parsed_url.query)
        album = query_params.get('album', ['unknown_album'])[0]
        image = query_params.get('image', ['unknown_image'])[0]

        filename = f"{album}_{image}".replace("/", "_").replace("&", "_").replace("?", "_")

        if not filename.lower().endswith('.jpg'):
            filename += '.jpg'

        file_path = os.path.join(save_dir, filename)

        img_response = await client.get(image_url)
        img_response.raise_for_status()

        with open(file_path, 'wb') as file:
            file.write(img_response.content)
        logger.info(f"Successfully downloaded {image_url}")
    except httpx.RequestError as e:
        logger.error(f"Failed to download image {image_url}: {e}")


async def download_images(urls: list[str], save_dir: str) -> None:
    async with httpx.AsyncClient() as client:
        tasks = [fetch_image(url, save_dir, client) for url in urls]
        await asyncio.gather(*tasks)


async def scrape_images(soup: BeautifulSoup) -> str:
    save_dir = get_tmp_dir_path()
    try:
        image_urls = await get_image_urls(soup)
        if not image_urls:
            logger.info("No images found to download.")
            return save_dir
        await download_images(image_urls, save_dir)
    except Exception as e:
        logger.error(f"Failed to scrape images: {e}")
        raise scrape_images_exception
    else:
        return save_dir


async def get_scraped_album_name(soup: BeautifulSoup) -> str:
    try:
        full_title = soup.title.string

        parts = full_title.split("»")
        if len(parts) > 1:
            album_name = parts[1].strip()
            album_name = album_name.replace("�", "").strip()
            return album_name
    except Exception as e:
        logger.error(f"Failed to get album name: {e}")
        return "Scraped Album"


async def scrape_and_save_images(url: str, user: str, album_id: str) -> tuple[list[str], str]:
    image_files = []
    save_dir = None
    try:
        soup = await get_soup(url)
        save_dir = await scrape_images(soup)
        album_name = await get_scraped_album_name(soup)
        album_id = await create_album(album_name, album_id)
        image_files = await prepare_image_files(save_dir)
        inserted_ids = await process_and_save_images(image_files, user, album_id)

        return inserted_ids, album_id
    except Exception as e:
        logger.error(f"Failed to scrape and save images: {e}")
        raise scrape_images_exception
    finally:
        await cleanup_files(image_files)
        shutil.rmtree(save_dir)


async def prepare_image_files(save_dir: str) -> list[UploadFile]:
    try:
        image_filenames = os.listdir(save_dir)
        image_files = []
        for filename in image_filenames:
            image_path = os.path.join(save_dir, filename)
            with open(image_path, 'rb') as file:
                contents = file.read()
            upload_file = UploadFile(filename=filename, file=BytesIO(contents))
            image_files.append(upload_file)

        return image_files
    except Exception as e:
        logger.error(f"Failed to prepare image files: {e}")
        raise prepare_image_files_exception


async def cleanup_files(image_files: list[UploadFile]) -> None:
    try:
        for file in image_files:
            file.file.close()
    except Exception as e:
        logger.error(f"Failed to cleanup files: {e}")
        raise clean_up_exception
