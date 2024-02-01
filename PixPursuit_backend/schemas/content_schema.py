from typing import List
from pydantic import BaseModel


class TagData(BaseModel):
    inserted_id: str
    tags: List[str]


class AlbumTagsData(BaseModel):
    album_id: str
    tags: List[str]


class FeedbackData(BaseModel):
    inserted_id: str
    tag: str
    is_positive: bool


class DescriptionData(BaseModel):
    inserted_id: str
    description: str


class LikeData(BaseModel):
    inserted_id: str
    is_positive: bool


class ViewData(BaseModel):
    inserted_id: str


class RemovingTagsData(BaseModel):
    image_id: str
    tags: List[str]


class FaceData(BaseModel):
    inserted_id: str
    anonymous_index: int
    name: str
