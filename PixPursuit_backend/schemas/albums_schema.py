from pydantic import BaseModel
from typing import Optional, List


class CreateAlbumData(BaseModel):
    album_name: str
    parent_id: Optional[str] = None
    image_ids: List[str] = []


class AddPhotosToAlbumData(BaseModel):
    album_id: str
    image_ids: List[str]


class DeleteAlbumData(BaseModel):
    album_id: str
