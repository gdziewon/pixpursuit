from typing import List, Optional
from pydantic import BaseModel


class TagData(BaseModel):
    inserted_id: str
    tags: List[str]


class SelectedTagsData(BaseModel):
    image_ids: Optional[str] = None
    album_ids: Optional[str] = None
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
