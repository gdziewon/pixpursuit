from typing import Optional, List
from pydantic import BaseModel


class ZipData(BaseModel):
    album_ids: Optional[List[str]] = []
    image_ids: Optional[List[str]] = []
