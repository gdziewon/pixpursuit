from datetime import timedelta
from fastapi import FastAPI, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict, Optional
import asyncio
from image_processing import process_image_async
from database_tools import save_to_database, add_tags, add_feedback, add_description, create_album, add_photos_to_album, get_album
from tag_prediction_tools import training_init
from logging_config import setup_logging
from celery_config import celery
from pydantic import BaseModel
from auth import authenticate_user, create_access_token, User, Token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

app = FastAPI()
celery.autodiscover_tasks(['tag_prediction_tools'])

logger = setup_logging()


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/process-images")
async def process_images_api(images: List[UploadFile] = [], album_id: str = None, current_user: User = Depends(get_current_user)):
    logger.info(f"/process-images endpoint accessed by {current_user['username']}")
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")

    processed_images = [asyncio.create_task(process_image_async(image)) for image in images]
    results = await asyncio.gather(*processed_images)

    inserted_ids = []
    for result in results:
        inserted_id = await save_to_database(result, current_user['username'], album_id)
        if inserted_id:
            inserted_ids.append(str(inserted_id))

    return {"inserted_ids": inserted_ids}


class TagData(BaseModel):
    inserted_id: str
    tags: List[str]


@app.post("/add-user-tag")
async def add_user_tag_api(data: TagData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-user-tags endpoint accessed by {current_user['username']}")
    success = await add_tags(data.tags, data.inserted_id)
    if success:
        await training_init(data.inserted_id)
        return {"message": "Tags added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add tags")


class FeedbackData(BaseModel):
    inserted_id: str
    feedback: Dict[str, bool]


@app.post("/feedback-on-tags")
async def feedback_on_tags_api(data: FeedbackData, current_user: User = Depends(get_current_user)):
    logger.info(f"/feedback-on-tags endpoint accessed by {current_user['username']}")
    success = await add_feedback(data.feedback, data.inserted_id)
    if success:
        await training_init(data.inserted_id)
        return {"message": "Feedback added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add feedback")


class DescriptionData(BaseModel):
    inserted_id: str
    description: str


@app.post("/add-description")
async def add_description_api(data: DescriptionData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-description endpoint accessed by {current_user['username']}")
    success = await add_description(data.description, data.inserted_id)
    if success:
        return {"message": "Description added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add description")


class CreateAlbumData(BaseModel):
    album_name: str
    parent_id: Optional[str] = None
    image_ids: List[str] = []


@app.post("/create-album")
async def create_album_api(data: CreateAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/create-album endpoint accessed by {current_user['username']}")

    album_name = data.album_name
    parent_id = data.parent_id
    image_ids = data.image_ids

    new_album_id = await create_album(album_name, parent_id)

    if image_ids:
        success = await add_photos_to_album(image_ids, new_album_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add photos to the new album")

    return {"message": "Album created successfully", "album_id": str(new_album_id)}


class AddPhotosToAlbumData(BaseModel):
    album_id: str
    image_ids: List[str]


@app.post("/add-photos-to-album")
async def add_photos_to_album_api(data: AddPhotosToAlbumData, current_user: User = Depends(get_current_user)):
    logger.info(f"/add-photos-to-album endpoint accessed by {current_user['username']}")

    album_id = data.album_id
    image_ids = data.image_ids

    if not image_ids:
        raise HTTPException(status_code=400, detail="No image IDs provided")

    album = await get_album(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    success = await add_photos_to_album(image_ids, album_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add photos to the album")

    return {"message": "Photos added to album successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
