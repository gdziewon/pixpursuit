"""
services/sharepoint/sharepoint_client.py

Defines a class to interact with SharePoint using Selenium for authentication and httpx for data retrieval.
Handles operations such as logging in to SharePoint, fetching folder contents, downloading images,
and processing SharePoint albums and files.
"""

import asyncio
import os
import httpx
import urllib.parse
from utils.dirs import get_tmp_dir_path
from data.databases.mongodb.async_db.database_tools import create_album
from data.data_extraction.image_processing import process_images_from_directory
from config.logging_config import setup_logging
from services.sharepoint.selenium_login import get_cookies
from celery import shared_task
from utils.function_utils import is_allowed_file
from utils.constants import API_URL, SHAREPOINT_FETCH_HEADERS, SHAREPOINT_TASK, MAIN_QUEUE

logger = setup_logging(__name__)


class SharePointClient:
    """
    A client for interacting with SharePoint to fetch and process album and image data.
    """
    def __init__(self, url: str, username: str, password: str, size: tuple[int, int] = None) -> None:
        """
        Initializes the SharePointClient with credentials and target URL.

        :param url: The full URL of the SharePoint site or folder to process.
        :param username: The username for SharePoint login.
        :param password: The password for SharePoint login.
        :param size: The size to which the images should be resized.
        """
        self.site_url = SharePointClient._extract_site_url(url)
        self.relative_url = SharePointClient._extract_relative_url(url)
        self.client = httpx.AsyncClient()
        self.cookies = SharePointClient._login(url, username, password)
        self.size = size
        logger.info(f"SharePoint client initialized with site URL: {self.site_url}")

    @staticmethod
    def _login(url: str, username: str, password: str) -> dict[str, str]:
        """
        Performs login to SharePoint and returns session cookies.

        :param url: The SharePoint site URL.
        :param username: The login username.
        :param password: The login password.
        :return: A dictionary of session cookies.
        """
        cookies = get_cookies(url, username, password)
        if not cookies:
            raise Exception("Failed to authenticate with SharePoint")
        return cookies

    @staticmethod
    def _extract_site_url(url: str) -> str:
        """
        Extracts the base site URL from a full SharePoint URL.

        :param url: The full SharePoint URL.
        :return: The base site URL.
        """
        parsed_url = urllib.parse.urlparse(url)
        path_elements = parsed_url.path.split('/')
        if 'sites' in path_elements:
            site_index = path_elements.index('sites')
            base_path = '/'.join(path_elements[:site_index + 2])
            return f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}"
        else:
            raise ValueError("Invalid SharePoint URL provided")

    @staticmethod
    def _extract_relative_url(url: str) -> str:
        """
        Extracts the relative URL from a full SharePoint URL.

        :param url: The full SharePoint URL.
        :return: The relative URL.
        """
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        folder_path = query_params.get('id', [None])[0]
        return folder_path

    async def _get_api_url(self, folder_path: str) -> str:
        """
        Constructs the API URL for accessing the SharePoint folder content.

        :param folder_path: The server relative URL of the SharePoint folder.
        :return: The full API URL for accessing the folder content.
        """
        if not folder_path:
            folder_path = self.relative_url

        api_url = API_URL.format(folder_path=folder_path)
        full_api_url = f"{self.site_url}{api_url}"
        return full_api_url

    async def _fetch_folder_contents(self, folder_path: str) -> dict[str, any]:
        """
        Fetches the contents of a SharePoint folder via the API.

        :param folder_path: The server relative URL of the folder to fetch.
        :return: A dictionary containing the fetched folder data.
        """
        api_url = await self._get_api_url(folder_path)
        response = await self.client.get(api_url, headers=SHAREPOINT_FETCH_HEADERS,
                                         cookies=self.cookies)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"SharePoint fetch failed: HTTP {response.status_code}")
            raise Exception(f"SharePoint fetch failed: HTTP {response.status_code}")

    async def process_sharepoint_album(self, user: str, folder_path: str = None, parent_id: str = None, album_name: str = None) -> None:
        """
        Processes a SharePoint album, creating a new album in the database and processing contained images and subfolders.

        :param user: The user performing the operation.
        :param folder_path: The path of the SharePoint folder to process.
        :param parent_id: The parent ID for the album in the database.
        :param album_name: The name of the album to create. If not provided, the name is derived from the URL.
        """
        try:
            folder_data = await self._fetch_folder_contents(folder_path)
            logger.info(f"Fetched folder contents for '{folder_path}'")

            if not album_name:
                album_name = self.relative_url.split('/')[-1]
            album_id = await create_album(album_name, parent_id)

            folder_data = folder_data.get('d', {})

            folders = folder_data.get('Folders', {}).get('results', [])
            for folder in folders:
                folder_name = folder.get('Name')
                folder_rel_path = folder.get('ServerRelativeUrl')
                await self.process_sharepoint_album(user, folder_rel_path, album_id, folder_name)

        except Exception as e:
            logger.error(f"Failed to fetch or process folder contents for '{folder_path}': {e}")
            return None

        files = folder_data.get('Files', {}).get('results', [])
        await self.process_sharepoint_files(files, user, album_id)

    async def process_sharepoint_files(self, files: list[dict], user: str, parent_id: str) -> None:
        """
        Processes a list of files from SharePoint, downloading them and initiating image processing.

        :param files: The list of files to process.
        :param user: The user performing the operation.
        :param parent_id: The parent ID for the files in the database.
        """
        save_dir = get_tmp_dir_path()
        try:
            await self._download_images(files, save_dir)
            await process_images_from_directory(save_dir, user, parent_id, self.size)

        except Exception as e:
            logger.error(f"Error processing sharepoint images: {e}")

    async def _download_image(self, file: dict, save_dir: str) -> None:
        """
        Downloads a single image from SharePoint and saves it to the specified directory.

        :param file: The file information dictionary.
        :param save_dir: The directory where the file should be saved.
        """
        file_url = file['__metadata']['uri'] + "/$value"
        filename = file_url.split('/')[-2][:-2]
        if not is_allowed_file(filename):
            logger.info(f"Skipping file {filename} as it is not an image")
            return

        img_response = await self.client.get(file_url, cookies=self.cookies)
        if img_response.status_code == 200:
            file_path = os.path.join(save_dir, filename)
            try:
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
            except Exception as e:
                logger.error(f"Failed to write file {filename}. Error: {e}")
        else:
            logger.error(f"Failed to download file {filename}. Status code: {img_response.status_code}")

    async def _download_images(self, files: list[dict], save_dir: str, max_concurrent_downloads: int = 10) -> None:
        """
        Downloads images from SharePoint and saves them locally.

        :param files: The list of files to download.
        :param save_dir: The directory where the files should be saved.
        """
        semaphore = asyncio.Semaphore(max_concurrent_downloads)

        async def download_with_semaphore(file):
            async with semaphore:
                await self._download_image(file, save_dir)

        tasks = [download_with_semaphore(file) for file in files]
        await asyncio.gather(*tasks)

    async def close(self) -> None:
        """
        Closes the HTTP client session.
        """
        await self.client.aclose()
        logger.info("HTTP client closed.")


@shared_task(name=SHAREPOINT_TASK, queue=MAIN_QUEUE)
def initiate_album_processing(sharepoint_url: str, sharepoint_username: str, sharepoint_password: str, user: str,
                              parent_id: str, size: tuple[int, int] = None) -> None:
    """
    Celery task to initiate the processing of a SharePoint album.

    :param sharepoint_url: The URL of the SharePoint site.
    :param sharepoint_username: The SharePoint username.
    :param sharepoint_password: The SharePoint password.
    :param user: The user initiating the process.
    :param parent_id: The parent album ID in the database.
    :param size: The size to which the images should be resized.
    """

    client = SharePointClient(sharepoint_url, sharepoint_username, sharepoint_password, size)
    loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.process_sharepoint_album(user, parent_id=parent_id))
    loop.run_until_complete(client.close())
    loop.close()
