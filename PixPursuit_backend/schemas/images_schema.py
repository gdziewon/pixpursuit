from typing import List, Optional
from pydantic import BaseModel


class DeleteImagesData(BaseModel):
    image_ids: List[str]


class RelocateImagesData(BaseModel):
    image_ids: Optional[List[str]] = None
    prev_album_id: str
    new_album_id: Optional[str] = None


class SimilarImagesData(BaseModel):
    image_id: str
    limit: Optional[int] = 10
