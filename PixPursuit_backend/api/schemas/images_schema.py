"""
api/schemas/images_schema.py

Contains Pydantic models for handling image data, including image upload, deletion,
and other image-related processes.
"""

from typing import List, Optional
from pydantic import BaseModel


class DeleteImagesData(BaseModel):
    """
    Schema for data required to delete images.

    :param image_ids: List of IDs of the images to be deleted.
    """
    image_ids: List[str]


class RelocateImagesData(BaseModel):
    """
    Schema for data required to relocate images.

    :param image_ids: List of IDs of the images to be relocated.
    :param prev_album_id: The current album ID from where images will be relocated.
    :param new_album_id: The target album ID to which images will be relocated.
    """
    image_ids: Optional[List[str]] = None
    prev_album_id: str
    new_album_id: Optional[str] = None


class SimilarImagesData(BaseModel):
    """
    Schema for data required to find similar images.

    :param image_id: The ID of the image to find similarities for.
    :param limit: The maximum number of similar images to return.
    """
    image_id: str
    limit: Optional[int] = 10


class ScrapeImagesData(BaseModel):
    """
    Schema for data required to scrape images from a URL.

    :param url: The URL from which images will be scraped.
    :param album_id: The album ID where the scraped images will be saved.
    """
    url: str
    album_id: Optional[str] = None
