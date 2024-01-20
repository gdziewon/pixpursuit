from datetime import timedelta
from fastapi import FastAPI, UploadFile, HTTPException, Depends, Form, File
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
import asyncio
from image_processing import process_image_async
from database_tools import save_image_to_database, add_tags, add_feedback, add_description, create_album, add_photos_to_album, get_album,\
                            remove_tags_from_image, delete_images, delete_album, relocate_to_album, add_names, add_like, add_view
from tag_prediction_tools import training_init, predict_and_update_tags
from logging_config import setup_logging
from pydantic import BaseModel
from celery_config import celery
from auth import authenticate_user, create_access_token, User, Token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
celery.autodiscover_tasks(['tag_prediction_tools', 'database_tools', 'object_detection', 'face_detection', 'feature_extraction'])
logger = setup_logging(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning("/token - Incorrect username or password")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    logger.info(f"/token - Successfully provided token to user: {user['username']}")
    return {"access_token": access_token, "token_type": "bearer", "username": user['username']}


@app.post("/process-images")
async def process_images_api(images: List[UploadFile] = File(...), album_id: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    logger.info(f"/process-images - Endpoint accessed by user: {current_user['username']}")

    if not images:
        logger.warning(f"/process-images - No images provided")
        raise HTTPException(status_code=400, detail="No images provided")

    processed_images = [asyncio.create_task(process_image_async(image)) for image in images]
    results = await asyncio.gather(*processed_images)
    logger.info(f"Album id: {album_id}")

    inserted_ids = []
    for result in results:
        inserted_id = await save_image_to_database(result, current_user['username'], album_id)
        if inserted_id:
            inserted_ids.append(inserted_id)

    predict_and_update_tags.delay(inserted_ids)
    logger.info(f"/process-images - Successfully processed and saved images: {inserted_ids}")
    return {"message": "Images saved successfully", "inserted_ids": inserted_ids}


class TagData(BaseModel):
    inserted_id: str
    tags: List[str]


@app.post("/add-user-tag")
async def add_user_tag_api(data: TagData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-user-tags - Endpoint accessed by user: {current_user['username']}")

    inserted_id = data.inserted_id
    tags = data.tags
    success = await add_tags(tags, inserted_id)
    if not success:
        logger.error("/add-user-tag - Failed to add tags")
        raise HTTPException(status_code=500, detail="Failed to add tags")

    logger.info(f"/add-user-tags - Successfully added tags to image: {inserted_id}")
    await training_init(inserted_id)
    return {"message": "Tags added successfully"}


class FeedbackData(BaseModel):
    inserted_id: str
    tag: str
    is_positive: bool


@app.post("/feedback-on-tags")
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


class DescriptionData(BaseModel):
    inserted_id: str
    description: str


@app.post("/add-description")
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


class LikeData(BaseModel):
    inserted_id: str
    is_positive: bool


@app.post("/add-like")
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


class ViewData(BaseModel):
    inserted_id: str


@app.post("/add-view")
async def add_view_api(data: ViewData):
    inserted_id = data.inserted_id
    success = await add_view(inserted_id)
    if not success:
        logger.error("/add-view - Failed to add view")
        raise HTTPException(status_code=500, detail="Failed to add view")

    logger.info(f"/add-view - Successfully added view to image: {inserted_id}")
    return {"message": "View added successfully"}


class CreateAlbumData(BaseModel):
    album_name: str
    parent_id: Optional[str] = None
    image_ids: List[str] = []


@app.post("/create-album")
async def create_album_api(data: CreateAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/create-album - Endpoint accessed by user: {current_user['username']}")

    album_name = data.album_name
    parent_id = data.parent_id
    image_ids = data.image_ids

    new_album_id = await create_album(album_name, parent_id)
    if not new_album_id:
        logger.error("/create-album - Failed to create new album")
        raise HTTPException(status_code=500, detail="Failed to create new album")

    logger.info(f"/create-album - Successfully created album: {str(new_album_id)}")

    if image_ids:
        success = await add_photos_to_album(image_ids, new_album_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add images to the new album")

        logger.info(f"/create-album - Successfully added images to new album: {str(new_album_id)}")

    return {"message": "Album created successfully", "album_id": str(new_album_id)}


class AddPhotosToAlbumData(BaseModel):
    album_id: str
    image_ids: List[str]


@app.post("/add-images-to-album")
async def add_images_to_album_api(data: AddPhotosToAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-images-to-album - Endpoint accessed by user: {current_user['username']}")

    album_id = data.album_id
    image_ids = data.image_ids

    if not image_ids:
        logger.warning("/add-images-to-album - No image IDs provided")
        raise HTTPException(status_code=400, detail="No image IDs provided")

    album = await get_album(album_id)
    if not album:
        logger.warning("/add-images-to-album - Album not found")
        raise HTTPException(status_code=404, detail="Album not found")

    success = await add_photos_to_album(image_ids, album_id)
    if not success:
        logger.error("/add-images-to-album - Failed to add photos to the album")
        raise HTTPException(status_code=500, detail="Failed to add photos to the album")

    logger.info(f"/add-images-to-album - Successfully added images to album: {str(album_id)}")
    return {"message": "Images added to album successfully"}


class RemovingTagsData(BaseModel):
    image_id: str
    tags: List[str]


@app.post("/remove-tags")
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


class DeleteImagesData(BaseModel):
    image_ids: List[str]


@app.delete("/delete-images")
async def delete_images_api(data: DeleteImagesData, current_user: User = Depends(get_current_user)):
    logger.info(f"/delete-images - Endpoint accessed by user: {current_user['username']}")

    image_ids = data.image_ids
    if not image_ids:
        logger.warning("/delete-images - No image IDs provided")
        raise HTTPException(status_code=400, detail="No image IDs provided")

    success = await delete_images(image_ids)
    if not success:
        logger.error("/delete-images - Failed to delete images")
        raise HTTPException(status_code=500, detail="Failed to delete images")

    logger.info(f"/delete-images - Successfully deleted images: {image_ids}")
    return {"message": "Images deleted successfully"}


class DeleteAlbumData(BaseModel):
    album_id: str


@app.delete("/delete-album")
async def delete_album_api(data: DeleteAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/delete-album  - Endpoint accessed by user: {current_user['username']}")

    album_id = data.album_id

    album = await get_album(album_id)
    if not album:
        logger.warning("/delete-album - Album not found")
        raise HTTPException(status_code=404, detail="Album not found")

    success = await delete_album(album_id)
    if not success:
        logger.error(f"/delete-album - Failed to delete album")
        raise HTTPException(status_code=500, detail="Failed to delete album")

    logger.info(f"/delete-album - Successfully deleted album: {album_id}")
    return {"message": "Album deleted successfully"}


class FaceData(BaseModel):
    inserted_id: str
    anonymous_index: int
    name: str


@app.post("/add-user-face")
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


class RelocateImagesData(BaseModel):
    image_ids: Optional[List[str]] = None
    prev_album_id: str
    new_album_id: Optional[str] = None


@app.post("/relocate-images")
async def relocate_images_api(data: RelocateImagesData, current_user: User = Depends(get_current_user)):
    logger.info(f"/relocate-images  - Endpoint accessed by user: {current_user['username']}")

    image_ids = data.image_ids
    prev_album_id = data.prev_album_id
    new_album_id = data.new_album_id

    album = await get_album(prev_album_id)
    if not album:
        logger.warning("/relocate-images - Album not found")
        raise HTTPException(status_code=404, detail="Album not found")

    success = await relocate_to_album(prev_album_id, new_album_id, image_ids,)
    if not success:
        logger.error("/relocate-images - Failed to relocate images")
        raise HTTPException(status_code=500, detail="Failed to relocate images")

    logger.info(f"Successfully relocated images from album: {prev_album_id}")
    return {"message": "Images relocated successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
