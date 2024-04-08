"""
services/image_scraper.py

Defines a class to scrape images from a given URL using BeautifulSoup for parsing HTML content.
The class provides functionality to download images and save them into a specified directory,
and process them into a specified album in the database.
"""

from bs4 import BeautifulSoup
from config.logging_config import setup_logging
import os
from utils.dirs import get_tmp_dir_path, cleanup_dir
from urllib.parse import urlparse, parse_qs, urljoin
from data.databases.mongodb.async_db.database_tools import create_album
from fastapi import UploadFile
from data.data_extraction.image_processing import process_and_save_images
from utils.function_utils import convert_to_upload_file
import httpx
import asyncio
from utils.constants import BASE_URL
from utils.exceptions import get_images_exception, get_soup_exception, scrape_images_exception, \
    clean_up_exception

logger = setup_logging(__name__)


class ImageScraper:
    """
    A scraper to download and process images from a webpage.
    """

    def __init__(self):
        """
        Initializes the ImageScraper with an async HTTP client.
        """
        self.client = httpx.AsyncClient()

    async def close(self):
        """
        Closes the HTTP client session.
        """
        await self.client.aclose()

    async def scrape_and_save_images(self, url: str, user: str, album_id: str) -> tuple[list[str], str]:
        """
        Main method to scrape images from the specified URL, save them, and process into an album.

        :param url: The URL to scrape images from.
        :param user: The user performing the scraping operation.
        :param album_id: The ID of the album where images will be saved.
        :return: The ID of the created or updated album containing the scraped images.
        """
        image_files = []
        save_dir = None
        try:
            soup = await self._get_soup(url)
            save_dir = await self._scrape_images(soup)
            album_name = await ImageScraper._get_scraped_album_name(soup)
            album_id = await create_album(album_name, album_id)
            image_files = await convert_to_upload_file(save_dir)
            await process_and_save_images(image_files, user, album_id)
            return album_id
        except Exception as e:
            logger.error(f"Failed to scrape and save images: {e}")
            raise scrape_images_exception
        finally:
            await ImageScraper._cleanup_files(image_files)
            cleanup_dir(save_dir)

    async def _get_soup(self, url: str) -> BeautifulSoup:
        """
        Fetches and parses the HTML content of a webpage into a BeautifulSoup object.

        :param url: The URL of the webpage to parse.
        :return: A BeautifulSoup object containing the parsed HTML content.
        """
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except httpx.RequestError as e:
            logger.error(f"Failed to get soup: {e}")
            raise get_soup_exception

    async def _fetch_image(self, image_url: str, save_dir: str) -> None:
        """
        Downloads an image from the specified URL and saves it to the given directory.

        :param image_url: The URL of the image to download.
        :param save_dir: The directory to save the downloaded image.
        """
        try:
            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)
            album = query_params.get('album', ['unknown_album'])[0]
            image = query_params.get('image', ['unknown_image'])[0]

            filename = f"{album}_{image}".replace("/", "_").replace("&", "_").replace("?", "_")

            if not filename.lower().endswith('.jpg'):
                filename += '.jpg'

            file_path = os.path.join(save_dir, filename)

            img_response = await self.client.get(image_url)
            img_response.raise_for_status()

            with open(file_path, 'wb') as file:
                file.write(img_response.content)
            logger.info(f"Successfully downloaded {image_url}")
        except httpx.RequestError as e:
            logger.error(f"Failed to download image {image_url}: {e}")

    async def _download_images(self, urls: list[str], save_dir: str) -> None:
        """
        Downloads images from the list of URLs and saves them to the specified directory.

        :param urls: A list of URLs of images to download.
        :param save_dir: The directory to save the downloaded images.
        """
        tasks = [self._fetch_image(url, save_dir) for url in urls]
        await asyncio.gather(*tasks)

    async def _scrape_images(self, soup: BeautifulSoup) -> str:
        """
        Scrapes image URLs from the given BeautifulSoup object and downloads them.

        :param soup: The BeautifulSoup object to scrape image URLs from.
        :return: The directory where the images are saved.
        """
        save_dir = get_tmp_dir_path()
        try:
            image_urls = await ImageScraper._get_image_urls(soup)
            if not image_urls:
                logger.info("No images found to download.")
                return save_dir
            await self._download_images(image_urls, save_dir)
        except Exception as e:
            logger.error(f"Failed to scrape images: {e}")
            raise scrape_images_exception
        else:
            return save_dir

    @staticmethod
    async def _get_image_urls(soup: BeautifulSoup) -> list[str]:
        """
        Extracts image URLs from the parsed HTML content.

        :param soup: The BeautifulSoup object containing the parsed HTML.
        :return: A list of image URLs extracted from the HTML content.
        """
        try:
            image_links = soup.find_all('a', attrs={'rel': 'lightbox-album'})
            full_image_urls = [urljoin(BASE_URL, link['href']) for link in image_links]
            return full_image_urls
        except Exception as e:
            logger.error(f"Failed to get image URLs: {e}")
            raise get_images_exception

    @staticmethod
    async def _get_scraped_album_name(soup: BeautifulSoup) -> str:
        """
        Extracts the album name from the webpage's title.

        :param soup: The BeautifulSoup object containing the parsed HTML.
        :return: The extracted album name.
        """
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

    @staticmethod
    async def _cleanup_files(image_files: list[UploadFile]) -> None:
        """
        Closes files to clean up resources.

        :param image_files: A list of UploadFile objects to be cleaned up.
        """
        try:
            for file in image_files:
                file.file.close()
        except Exception as e:
            logger.error(f"Failed to cleanup files: {e}")
            raise clean_up_exception
