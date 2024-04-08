"""
api/schemas/albums_schema.py

Contains Pydantic models for album-related operations like creating, renaming, and
deleting albums, as well as managing album contents.
"""

from pydantic import BaseModel
from typing import Optional, List


class CreateAlbumData(BaseModel):
    """
    Schema for creating a new album.

    :param album_name: Name of the album to create.
    :param parent_id: ID of the parent album, if any.
    :param image_ids: List of image IDs to initially add to the album.
    """
    album_name: str
    parent_id: Optional[str] = None
    image_ids: List[str] = []


class AddPhotosToAlbumData(BaseModel):
    """
    Schema for adding photos to an album.

    :param album_id: ID of the album where photos will be added.
    :param image_ids: List of image IDs to add to the album.
    """
    album_id: str
    image_ids: List[str]


class DeleteAlbumsData(BaseModel):
    """
    Schema for deleting albums.

    :param album_ids: List of album IDs to be deleted.
    """
    album_ids: List[str]


class RenameAlbumData(BaseModel):
    """
    Schema for renaming an album.

    :param album_id: ID of the album to be renamed.
    :param new_name: New name for the album.
    """
    album_id: str
    new_name: str


class SharepointUploadData(BaseModel):
    """
    Schema for uploading data to SharePoint.

    :param sharepoint_url: URL of the SharePoint site to upload files.
    :param sharepoint_username: Username for SharePoint authentication.
    :param sharepoint_password: Password for SharePoint authentication.
    :param parent_id: Optional parent ID for the uploaded content.
    :param size: Optional size (width, height) for processing the uploaded images.
    """
    sharepoint_url: str
    sharepoint_username: str
    sharepoint_password: str
    parent_id: Optional[str] = None
    size: Optional[tuple[int, int]] = None
