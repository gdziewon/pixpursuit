import asyncio
import os
import httpx
import urllib.parse
from utils.dirs import get_tmp_dir_path
from data.databases.database_tools import create_album
from data.data_extraction.image_processing import process_images_from_directory
from config.logging_config import setup_logging
from utils.selenium_login import get_cookies
from celery import shared_task
from utils.function_utils import is_allowed_file

logger = setup_logging(__name__)


class SharePointClient:
    def __init__(self, url: str, username: str, password: str, size: tuple[int, int] = None) -> None:
        self.site_url = SharePointClient.extract_site_url(url)
        self.relative_url = SharePointClient.extract_relative_url(url)
        self.client = httpx.AsyncClient()
        self.cookies = SharePointClient.login(url, username, password)
        self.size = size
        logger.info(f"SharePoint client initialized with site URL: {self.site_url}")

    @staticmethod
    def login(url: str, username: str, password: str) -> dict[str, str]:
        cookies = get_cookies(url, username, password)
        if not cookies:
            raise Exception("Failed to authenticate with SharePoint")
        return cookies

    @staticmethod
    def extract_site_url(url: str) -> str:
        parsed_url = urllib.parse.urlparse(url)
        path_elements = parsed_url.path.split('/')
        if 'sites' in path_elements:
            site_index = path_elements.index('sites')
            base_path = '/'.join(path_elements[:site_index + 2])
            return f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}"
        else:
            raise ValueError("Invalid SharePoint URL provided")

    @staticmethod
    def extract_relative_url(url: str) -> str:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        folder_path = query_params.get('id', [None])[0]
        return folder_path

    async def get_api_url(self, folder_path: str) -> str:
        if not folder_path:
            folder_path = self.relative_url

        api_url = f"/_api/web/GetFolderByServerRelativeUrl('{folder_path}')?$expand=Folders,Files"
        full_api_url = f"{self.site_url}{api_url}"
        return full_api_url

    async def fetch_folder_contents(self, folder_path: str) -> dict[str, any]:
        api_url = await self.get_api_url(folder_path)
        response = await self.client.get(api_url, headers={"Accept": "application/json;odata=verbose"},
                                         cookies=self.cookies)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"SharePoint fetch failed: HTTP {response.status_code}")
            raise Exception(f"SharePoint fetch failed: HTTP {response.status_code}")

    async def process_sharepoint_album(self, user: str, folder_path: str = None, parent_id: str = None, album_name: str = None) -> None:
        try:
            folder_data = await self.fetch_folder_contents(folder_path)
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
        save_dir = get_tmp_dir_path()
        try:
            await self.download_images(files, save_dir)
            await process_images_from_directory(save_dir, user, parent_id, self.size)

        except Exception as e:
            logger.error(f"Error processing sharepoint images: {e}")

    async def download_image(self, file: dict, save_dir: str) -> None:
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

    async def download_images(self, files: list[dict], save_dir: str, max_concurrent_downloads: int = 10) -> None:
        semaphore = asyncio.Semaphore(max_concurrent_downloads)

        async def download_with_semaphore(file):
            async with semaphore:
                await self.download_image(file, save_dir)

        tasks = [download_with_semaphore(file) for file in files]
        await asyncio.gather(*tasks)

    async def close(self) -> None:
        await self.client.aclose()
        logger.info("HTTP client closed.")


@shared_task(name="sharepoint_client.initiate_album_processing.main", queue="main_queue")
def initiate_album_processing(sharepoint_url: str, sharepoint_username: str, sharepoint_password: str, user: str,
                              parent_id: str, size: tuple[int, int] = None) -> None:
    client = SharePointClient(sharepoint_url, sharepoint_username, sharepoint_password, size)
    loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.process_sharepoint_album(user, parent_id=parent_id))
    loop.run_until_complete(client.close())
    loop.close()
