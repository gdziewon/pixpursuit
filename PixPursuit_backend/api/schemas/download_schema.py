"""
api/schemas/download_schema.py

Provides Pydantic models for download-related operations, primarily for constructing
requests for downloading images or albums as zip files.
"""

from typing import Optional, List
from pydantic import BaseModel


class ZipData(BaseModel):
    """
    Schema for data required to download a zip file.

    :param album_ids: Optional list of album IDs to include in the zip.
    :param image_ids: Optional list of image IDs to include in the zip.
    """
    album_ids: Optional[List[str]] = []
    image_ids: Optional[List[str]] = []
