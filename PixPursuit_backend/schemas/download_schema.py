from typing import Optional, List
from pydantic import BaseModel


class DownloadData(BaseModel):
    url: str


class ZipData(BaseModel):
    album_ids: Optional[List[str]] = []
    image_ids: Optional[List[str]] = []