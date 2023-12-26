import torch
import torch.optim as optim
from celery_config import celery
import logging
import os
import asyncio
from tag_prediction_model import TagPredictor
from database_tools import get_image_document, get_unique_tags, add_auto_tags, get_image_ids_paginated

logger = logging.getLogger(__name__)

MODEL_FILE_PATH = os.getenv('MODEL_FILE_PATH', 'tag_predictor_state.pth')
LEARNING_RATE = float(os.getenv('LEARNING_RATE', '0.001'))


def save_model_state(model, file_path=MODEL_FILE_PATH):
    try:
        torch.save(model.state_dict(), file_path)
        logger.info("Model state saved")
    except Exception as e:
        logger.error(f"Error saving model state: {e}", exc_info=True)


def load_model_state(file_path=MODEL_FILE_PATH, input_size=1000, hidden_size=512, num_tags=1):
    try:
        model = TagPredictor(input_size, hidden_size, num_tags)
        model.load_state_dict(torch.load(file_path))
        logger.info("Model state loaded")
        return model
    except Exception as e:
        logger.error(f"Error loading model state: {e}", exc_info=True)
        return None


async def update_model_tags():
    try:
        tag_predictor = load_model_state()
        unique_tags = await get_unique_tags()
        num_tags = len(unique_tags)
        if num_tags != tag_predictor.fc3.out_features:
            tag_predictor.update_output_layer(num_tags)
            save_model_state(tag_predictor)
            logger.info(f"Model output layer updated to match the number of unique tags: {num_tags}")
    except Exception as e:
        logger.error(f"Error updating model tags: {e}", exc_info=True)


async def tags_to_vector(tags, feedback):
    try:
        unique_tags = await get_unique_tags()
        tag_vector = [0] * len(unique_tags)
        tag_dict = {tag: i for i, tag in enumerate(unique_tags)}

        for tag in tags:
            if tag in tag_dict:
                tag_vector[tag_dict[tag]] = 1

        for tag, value in feedback.items():
            if tag in tag_dict and tag not in tags:
                tag_vector[tag_dict[tag]] = int(value)

        return tag_vector
    except Exception as e:
        logger.error(f"Error converting tags to vector: {e}", exc_info=True)
        return []


async def training_init(inserted_id):
    try:
        image_document = await get_image_document(inserted_id)
        if image_document:
            features = image_document['features']
            feedback_tags = image_document.get('feedback', {})
            tags = image_document['user_tags']
            await update_model_tags()
            tag_vector = await tags_to_vector(tags, feedback_tags)
            train_model.delay(features, tag_vector)
            logger.info(f"Training initialized for image: {inserted_id}")
    except Exception as e:
        logger.error(f"Error during training initialization: {e}", exc_info=True)


async def predictions_to_tag_names(predictions):
    all_tags = await get_unique_tags()
    index_to_tag = {i: tag['name'] for i, tag in enumerate(all_tags)}
    return [index_to_tag[idx] for idx in predictions if idx in index_to_tag]


@celery.task(name='tag_prediction_tools.train_model')
def train_model(features, tag_vector):
    tag_predictor = load_model_state()
    if not tag_predictor:
        logger.error("Model loading failed, training aborted.")
        return

    features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    target = torch.tensor([tag_vector], dtype=torch.float32)

    criterion = torch.nn.BCELoss()
    optimizer = optim.Adam(tag_predictor.parameters(), lr=LEARNING_RATE)

    predicted_tags = tag_predictor(features_tensor)
    loss = criterion(predicted_tags, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    save_model_state(tag_predictor)
    logger.info("Model trained and state saved")


@celery.task(name='tag_prediction_tools.predict_and_update_tags')
def predict_and_update_tags(image_id, features):
    logger.info(f"Predicting and updating tags")
    tag_predictor = load_model_state()
    if not tag_predictor:
        logger.error("Model loading failed, prediction aborted.")
        return

    async def async_task():
        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        predicted_indices = tag_predictor.predict_tags(features_tensor)
        predicted_tags = await predictions_to_tag_names(predicted_indices)
        await add_auto_tags(image_id, predicted_tags)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())


@celery.task(name='tag_prediction_tools.update_all_auto_tags')
def update_all_auto_tags():
    try:
        loop = asyncio.get_event_loop()
        page_number = 1
        page_size = 100
        while True:
            image_ids = loop.run_until_complete(get_image_ids_paginated(page_number, page_size))
            if not image_ids:
                break

            for image_id in image_ids:
                image_document = loop.run_until_complete(get_image_document(image_id))
                if image_document:
                    features = image_document['features']
                    predict_and_update_tags.delay(image_id, features)

            page_number += 1
    except Exception as e:
        logger.error(f"Error in update_all_auto_tags: {e}")
