from pydantic import BaseModel
from typing import Optional, List


class CreateAlbumData(BaseModel):
    album_name: str
    parent_id: Optional[str] = None
    image_ids: List[str] = []


class AddPhotosToAlbumData(BaseModel):
    album_id: str
    image_ids: List[str]


class DeleteAlbumsData(BaseModel):
    album_ids: List[str]


class RenameAlbumData(BaseModel):
    album_id: str
    new_name: str
