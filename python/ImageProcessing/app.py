from fastapi import FastAPI, UploadFile, HTTPException, Form
from typing import List, Dict
import asyncio
from image_processing import process_image_async
from database_tools import save_to_database, add_tags, add_feedback, add_description
from tag_prediction_model import TagPredictor
from tag_prediction_tools import update_model_tags, added_tag_training_init, feedback_training_init, save_model_state
from logging_config import setup_logging
from celery import Celery
from pydantic import BaseModel

tag_predictor = TagPredictor(input_size=1000, hidden_size=512, num_tags=1)
save_model_state(tag_predictor)

app = FastAPI()
celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
celery.autodiscover_tasks(['database_tools', 'tag_prediction_tools'])

logger = setup_logging()


@app.post("/process-images")
async def process_images_api(images: List[UploadFile] = []):
    logger.info("/process-images endpoint accessed")
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")

    processed_images = [asyncio.create_task(process_image_async(image)) for image in images]
    results = await asyncio.gather(*processed_images)

    inserted_ids = []
    for result in results:
        inserted_id = await save_to_database(result)
        if inserted_id:
            inserted_ids.append(str(inserted_id))

    return {"inserted_ids": inserted_ids}


@app.post("/add-user-tag")
async def add_user_tag_api(inserted_id: str = Form(...), tags: List[str] = Form(...)):
    logger.info("/add-user-tags endpoint accessed")
    success = await add_tags(tags, inserted_id)
    if success:
        await update_model_tags()
        await added_tag_training_init(inserted_id)
        return {"message": "Tags added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add tags")


class FeedbackData(BaseModel):
    inserted_id: str
    feedback: Dict[str, bool]


@app.post("/feedback-on-tags")
async def feedback_on_tags_api(data: FeedbackData):
    logger.info("/feedback-on-tags endpoint accessed")
    inserted_id = data.inserted_id
    feedback = data.feedback
    success = await add_feedback(feedback, inserted_id)
    if success:
        await feedback_training_init(inserted_id)
        return {"message": "Feedback added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add feedback")


@app.post("/add-description")
async def add_description_api(inserted_id: str = Form(...), description: str = Form(...)):
    logger.info("/add-description endpoint accessed")
    success = await add_description(description, inserted_id)
    if success:
        return {"message": "Description added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add description")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
