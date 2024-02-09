from config.logging_config import setup_logging
from databases.database_tools import get_image_document, save_image_to_database, get_album, create_album, add_photos_to_album
import requests


class SharePointClient:
    def __init__(self):
        self.logger = setup_logging(__name__)

    def make_request(self, method, endpoint, sharepoint_url, access_token, data=None):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose"
        }
        url = f"{sharepoint_url}/_api/{endpoint}"
        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None

    async def copy_images_to_sharepoint(self, image_ids, folder_name, sharepoint_url, access_token):
        for image_id in image_ids:
            try:
                image = await get_image_document(image_id)
                if not image:
                    self.logger.warning(f"Image not found: {image_id}")
                    continue

                endpoint = f"web/getfolderbyserverrelativeurl('{folder_name}')/files/add(url='{image['filename']}',overwrite=true)"
                response = self.make_request("POST", endpoint, sharepoint_url, access_token, data=image['file_content'])
                if response is None:
                    self.logger.error(f"Failed to upload image: {image_id}")
                    continue

                self.logger.info(f"Image uploaded: {image_id}")
            except Exception as e:
                self.logger.error(f"Error copying image to SharePoint: {e}")

    async def copy_images_from_sharepoint(self, items, folder_name, sharepoint_url, access_token):
        inserted_ids = []
        for item in items:
            try:
                item_id, file_name = item

                endpoint = f"web/getfilebyserverrelativeurl('{folder_name}/{file_name}')/$value"
                file_content = self.make_request("GET", endpoint, sharepoint_url, access_token)
                if file_content is None:
                    self.logger.error(f"Failed to download image: {file_name}")
                    continue

                with open(file_name, 'wb') as file:
                    file.write(file_content)

                image_data = {
                    'filename': file_name,
                    'file_path': file_name,
                    # other necessary image data here
                }
                inserted_id = await save_image_to_database(image_data, 'sharepoint', None)
                if inserted_id:
                    inserted_ids.append(inserted_id)

                self.logger.info(f"Image downloaded: {file_name}")
            except Exception as e:
                self.logger.error(f"Error copying image from SharePoint: {e}")

        return inserted_ids if inserted_ids else False

    async def copy_album_to_sharepoint(self, album_id, folder_name, sharepoint_url, access_token):
        try:
            album = await get_album(album_id)
            if not album:
                self.logger.error(f"Album not found: {album_id}")
                return False

            image_ids = album['image_ids']
            await self.copy_images_to_sharepoint(image_ids, folder_name, sharepoint_url, access_token)

            for nested_album_id in album['sons']:
                await self.copy_album_to_sharepoint(nested_album_id, folder_name + '/' + nested_album_id, sharepoint_url, access_token)

            self.logger.info(f"Album copied to SharePoint: {album_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error copying album to SharePoint: {e}")
            return False

    async def copy_album_from_sharepoint(self, folder_name, sharepoint_url, access_token):
        try:
            endpoint = f"web/getfolderbyserverrelativeurl('{folder_name}')"
            folder = self.make_request("GET", endpoint, sharepoint_url, access_token)
            if folder is None:
                self.logger.error(f"Failed to retrieve folder: {folder_name}")
                return False

            files = folder['Files']['results']
            items = [(file['UniqueId'], file['Name']) for file in files]
            inserted_ids = await self.copy_images_from_sharepoint(items, folder_name, sharepoint_url, access_token)
            if not inserted_ids:
                return False

            new_album_id = await create_album(folder_name.split('/')[-1])
            await add_photos_to_album(inserted_ids, new_album_id)

            for nested_folder in folder['Folders']['results']:
                await self.copy_album_from_sharepoint(nested_folder['ServerRelativeUrl'], sharepoint_url, access_token)

            self.logger.info(f"Album copied from SharePoint: {folder_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error copying album from SharePoint: {e}")
            return False
