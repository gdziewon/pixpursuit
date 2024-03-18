from fastapi import APIRouter, Depends
from data.databases.database_tools import add_tags_to_images, add_tags_to_albums, add_feedback, add_description, add_like, \
    add_view, remove_tags_from_image, add_names
from services.authentication.auth import get_current_user
from services.tag_prediction.tag_prediction_tools import training_init, train_init_albums
from api.schemas.content_schema import TagData, FeedbackData, DescriptionData, LikeData, ViewData, SelectedTagsData, \
    RemovingTagsData, FaceData
from api.schemas.auth_schema import User
from utils.exceptions import add_tags_exception, no_image_and_album_ids_exception, add_names_exception, \
    add_feedback_exception, add_description_exception, add_like_exception, add_view_exception, remove_tags_exception

router = APIRouter()


@router.post("/add-user-tag")
async def add_user_tag_api(data: TagData, current_user: User = Depends(get_current_user)):
    success = await add_tags_to_images(data.tags, [data.inserted_id])
    if not success:
        raise add_tags_exception
    await training_init([data.inserted_id])
    return {"message": "Tags added successfully"}


@router.post("/add-tags-to-selected")
async def add_tags_to_selected_api(data: SelectedTagsData, current_user: User = Depends(get_current_user)):
    if not data.image_ids and not data.album_ids:
        raise no_image_and_album_ids_exception
    success = (await add_tags_to_images(data.tags, data.image_ids) and
               await add_tags_to_albums(data.tags, data.album_ids))
    if not success:
        raise add_tags_exception
    await training_init(data.image_ids)
    await train_init_albums(data.album_ids)
    return {"message": "Tags added to selected items successfully"}


@router.post("/feedback-on-tags")
async def feedback_on_tags_api(data: FeedbackData, current_user: User = Depends(get_current_user)):
    success = await add_feedback(data.tag, data.is_positive, current_user.username, data.inserted_id)
    if not success:
        raise add_feedback_exception
    await training_init([data.inserted_id])
    return {"message": "Feedback added successfully"}


@router.post("/add-description")
async def add_description_api(data: DescriptionData, current_user: User = Depends(get_current_user)):
    success = await add_description(data.description, data.inserted_id)
    if not success:
        raise add_description_exception
    return {"message": "Description added successfully"}


@router.post("/add-like")
async def add_like_api(data: LikeData, current_user: User = Depends(get_current_user)):
    success = await add_like(data.is_positive, current_user.username, data.inserted_id)
    if not success:
        raise add_like_exception
    return {"message": "Like added successfully"}


@router.post("/add-view")
async def add_view_api(data: ViewData):
    success = await add_view(data.inserted_id)
    if not success:
        raise add_view_exception
    return {"message": "View added successfully"}


@router.post("/remove-tags")
async def remove_tags_api(data: RemovingTagsData, current_user: User = Depends(get_current_user)):
    success = await remove_tags_from_image(data.image_id, data.tags)
    if not success:
        raise remove_tags_exception
    await training_init([data.image_id])
    return {"message": "Tags removed successfully"}


@router.post("/add-user-face")
async def add_user_face_api(data: FaceData, current_user: User = Depends(get_current_user)):
    success = await add_names(data.inserted_id, data.anonymous_index, data.name)
    if not success:
        raise add_names_exception
    return {"message": "Name added successfully"}
