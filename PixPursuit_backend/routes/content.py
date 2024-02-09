from fastapi import APIRouter, Depends, HTTPException
from config.logging_config import setup_logging
from databases.database_tools import add_tags_to_images, add_feedback, add_description, add_like, add_view, remove_tags_from_image, add_tags_to_albums
from databases.face_operations import add_names
from authentication.auth import get_current_user
from tag_prediction.tag_prediction_tools import training_init
from schemas.content_schema import TagData, FeedbackData, DescriptionData, LikeData, ViewData, RemovingTagsData, FaceData, SelectedTagsData
from schemas.auth_schema import User

router = APIRouter()
logger = setup_logging(__name__)


@router.post("/add-user-tag")
async def add_user_tag_api(data: TagData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-user-tags - Endpoint accessed by user: {current_user['username']}")

    inserted_id = data.inserted_id
    tags = data.tags
    success = await add_tags_to_images(tags, [inserted_id])
    if not success:
        logger.error("/add-user-tag - Failed to add tags")
        raise HTTPException(status_code=500, detail="Failed to add tags")

    logger.info(f"/add-user-tags - Successfully added tags to image: {inserted_id}")
    await training_init(inserted_id)
    return {"message": "Tags added successfully"}


@router.post("/add-tags-to-selected")
async def add_tags_to_selected_api(data: SelectedTagsData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-tags-to-selected - Endpoint accessed by user: {current_user['username']}")

    image_ids = data.image_ids
    album_ids = data.album_ids
    tags = data.tags
    if not image_ids and not album_ids:
        logger.warning("/add-tags-to-selected - No image IDs or album IDs provided")
        raise HTTPException(status_code=400, detail="No image IDs or album IDs provided")

    success = await add_tags_to_images(tags, image_ids) and await add_tags_to_albums(tags, album_ids)

    if not success:
        logger.error("/add-tags-to-selected - Failed to add tags to selected items")
        raise HTTPException(status_code=500, detail="Failed to add tags to selected items")

    logger.info(f"/add-tags-to-selected - Successfully added tags to selected items")
    return {"message": "Tags added to selected items successfully"}


@router.post("/feedback-on-tags")
async def feedback_on_tags_api(data: FeedbackData, current_user: User = Depends(get_current_user)):
    logger.info(f"/feedback-on-tags - Endpoint accessed by user: {current_user['username']}")

    inserted_id = data.inserted_id
    tag = data.tag
    is_positive = data.is_positive
    success = await add_feedback(tag, is_positive, current_user['username'], inserted_id)
    if not success:
        logger.error("/feedback-on-tags - Failed to add feedback")
        raise HTTPException(status_code=500, detail="Failed to add feedback")

    await training_init(inserted_id)
    logger.info(f"/feedback-on-tags - Successfully added feedback to image: {inserted_id}")
    return {"message": "Feedback added successfully"}


@router.post("/add-description")
async def add_description_api(data: DescriptionData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-description - Endpoint accessed by user: {current_user['username']}")

    inserted_id = data.inserted_id
    description = data.description
    success = await add_description(description, inserted_id)
    if not success:
        logger.error("/add-description - Failed to add description")
        raise HTTPException(status_code=500, detail="Failed to add description")

    logger.info(f"/add-description - Successfully added description to image: {inserted_id}")
    return {"message": "Description added successfully"}


@router.post("/add-like")
async def add_like_api(data: LikeData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-like - Endpoint accessed by user: {current_user['username']}")

    inserted_id = data.inserted_id
    is_positive = data.is_positive
    success = await add_like(is_positive, current_user['username'], inserted_id)
    if not success:
        logger.error("/add-like - Failed to add like")
        raise HTTPException(status_code=500, detail="Failed to add like")

    logger.info(f"/add-like - Successfully added like to image: {inserted_id}")
    return {"message": "Like added successfully"}


@router.post("/add-view")
async def add_view_api(data: ViewData):
    inserted_id = data.inserted_id
    success = await add_view(inserted_id)
    if not success:
        logger.error("/add-view - Failed to add view")
        raise HTTPException(status_code=500, detail="Failed to add view")

    logger.info(f"/add-view - Successfully added view to image: {inserted_id}")
    return {"message": "View added successfully"}


@router.post("/remove-tags")
async def remove_tags_api(data: RemovingTagsData, current_user: User = Depends(get_current_user)):
    logger.info(f"/remove-tags -  Endpoint accessed by user: {current_user['username']}")

    image_id = data.image_id
    tags_to_remove = data.tags
    if not image_id:
        logger.warning("/remove-tags - No image IDs provided")
        raise HTTPException(status_code=400, detail="No image IDs provided")

    success = await remove_tags_from_image(image_id, tags_to_remove)
    if not success:
        logger.error("/remove-tags - Failed to add photos to the album")
        raise HTTPException(status_code=500, detail="Failed to add photos to the album")

    logger.info(f"remove-tags - Successfully removed tags from image: {image_id}")
    await training_init(image_id)
    return {"message": "Tags removed successfully"}


@router.post("/add-user-face")
async def add_user_face_api(data: FaceData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-user-faces - Endpoint accessed by user: {current_user['username']}")

    inserted_id = data.inserted_id
    anonymous_index = data.anonymous_index
    name = data.name
    success = await add_names(inserted_id, anonymous_index, name)
    if not success:
        logger.error("/add-user-faces - Failed to add faces")
        raise HTTPException(status_code=500, detail="Failed to add faces")

    logger.info(f"/add-user-faces - Successfully added name to face: {inserted_id}")
    return {"message": "Name added successfully"}
