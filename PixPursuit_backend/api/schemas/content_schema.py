"""
api/schemas/content_schema.py

Defines Pydantic models for content management, such as tagging, feedback submission,
and other content-related interactions within the application.
"""

from typing import List, Optional
from pydantic import BaseModel


class TagData(BaseModel):
    """
    Schema for tagging image.

    :param inserted_id: ID of the image or album to which tags are added.
    :param tags: A list of tags to be added.
    """
    inserted_id: str
    tags: List[str]


class SelectedTagsData(BaseModel):
    """
    Schema for adding tags to selected images and albums.

    :param album_ids: Optional list of album IDs to which tags will be added.
    :param image_ids: Optional list of image IDs to which tags will be added.
    :param tags: A list of tags to be added.
    """
    album_ids: Optional[List[str]] = []
    image_ids: Optional[List[str]] = []
    tags: List[str]


class FeedbackData(BaseModel):
    """
    Schema for feedback on tags.

    :param inserted_id: ID of the image or album to which feedback is related.
    :param tag: The tag for which feedback is given.
    :param is_positive: Boolean indicating whether the feedback is positive or negative.
    """
    inserted_id: str
    tag: str
    is_positive: bool


class DescriptionData(BaseModel):
    """
    Schema for adding a description to an image or album.

    :param inserted_id: ID of the image or album to which the description is added.
    :param description: Textual description to be added.
    """
    inserted_id: str
    description: str


class LikeData(BaseModel):
    """
    Schema for liking an image.

    :param inserted_id: ID of the image being liked.
    :param is_positive: Boolean indicating like (true) or dislike (false).
    """
    inserted_id: str
    is_positive: bool


class ViewData(BaseModel):
    """
    Schema for adding a view to an image or album.

    :param inserted_id: ID of the image or album being viewed.
    """
    inserted_id: str


class RemovingTagsData(BaseModel):
    """
    Schema for removing tags from an image.

    :param image_id: ID of the image from which tags will be removed.
    :param tags: List of tags to be removed.
    """
    image_id: str
    tags: List[str]


class FaceData(BaseModel):
    """
    Schema for face data associated with an image.

    :param inserted_id: ID of the image to which the face data is added.
    :param anonymous_index: Index of the anonymous face in the image.
    :param name: Name to be associated with the face.
    """
    inserted_id: str
    anonymous_index: int
    name: str
