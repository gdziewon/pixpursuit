"""
services/tag_prediction/tag_prediction_tools.py

This module contains functions and tasks related to the training and prediction processes of a machine learning model for tag prediction.
It includes caching mechanisms for unique tags, model state management, and Celery tasks for asynchronous training and prediction operations.
"""

import torch
import torch.optim as optim
from config.logging_config import setup_logging
import os
from celery import shared_task
from services.tag_prediction.tag_predictor import TagPredictor
from data.databases.mongodb.async_db.database_tools import get_image_document
from data.databases.mongodb.sync_db.celery_database_tools import get_image_document_sync, get_unique_tags, add_auto_tags, get_image_ids_paginated
from data.databases.mongodb.async_db.database_tools import get_album
from utils.constants import (
    POSITIVE_THRESHOLD, LEARNING_RATE, MODEL_FILE_PATH, TRAIN_MODEL_TASK,
    PREDICT_TAGS_TASK, PREDICT_ALL_TAGS_TASK, MAIN_QUEUE, BEAT_QUEUE
)

logger = setup_logging(__name__)

unique_tags_cache = None


def get_unique_tags_cached() -> list[str]:
    """
    Retrieves and caches the unique tags. If already cached, returns the cached tags.

    :return: A list of unique tags.
    """
    global unique_tags_cache
    if unique_tags_cache is None:
        unique_tags_cache = get_unique_tags()
    return unique_tags_cache


def update_unique_tags_cache() -> None:
    """
    Updates the cache of unique tags.
    """
    global unique_tags_cache
    unique_tags_cache = get_unique_tags()


def save_model_state(model: TagPredictor, file_path: str = MODEL_FILE_PATH) -> None:
    """
    Saves the state of the tag prediction model to a file.

    :param model: The TagPredictor model to save.
    :param file_path: The path to the file where the model state should be saved.
    """
    try:
        torch.save({
            'state_dict': model.state_dict(),
            'num_tags': model.num_tags
        }, file_path)
    except Exception as e:
        logger.error(f"Error saving model state: {e}", exc_info=True)


def load_model_state(file_path: str = MODEL_FILE_PATH, input_size: int = 1000,
                     hidden_size: int = 512) -> TagPredictor or None:
    """
    Loads the tag prediction model from a file.

    :param file_path: The path to the file from which the model state should be loaded.
    :param input_size: The input size for the model.
    :param hidden_size: The hidden size for the model.
    :return: The loaded TagPredictor model, or None if loading fails.
    """
    if not os.path.exists(file_path):
        logger.warning(f"Model file {file_path} not found. Initializing a new model.")
        tag_predictor = TagPredictor(input_size, hidden_size, len(get_unique_tags_cached()))
        return tag_predictor

    try:
        checkpoint = torch.load(file_path)
        num_tags = checkpoint['num_tags']
        model = TagPredictor(input_size, hidden_size, num_tags)
        model.load_state_dict(checkpoint['state_dict'])
        return model
    except Exception as e:
        logger.error(f"Error loading model state: {e}", exc_info=True)
        return None


def update_model_tags(tag_vector: list[int] = None) -> TagPredictor:
    """
    Updates the tags of the model based on the provided tag vector.

    :param tag_vector: A list of integers representing the tag vector.
    :return: The updated TagPredictor model.
    """
    tag_predictor = load_model_state()
    try:
        if not tag_vector:
            unique_tags = get_unique_tags_cached()
            num_tags = len(unique_tags)
        else:
            num_tags = len(tag_vector)
        if num_tags != tag_predictor.fc3.out_features:
            tag_predictor.update_output_layer(num_tags)
    except Exception as e:
        logger.error(f"Error updating model tags: {e}", exc_info=True)

    save_model_state(tag_predictor)
    return tag_predictor


def tags_to_vector(tags: list[str], feedback: dict) -> list[int]:
    """
    Converts a list of tags and their feedback to a vector representation.

    :param tags: A list of tags.
    :param feedback: A dictionary containing feedback data.
    :return: A list of integers representing the tag vector.
    """
    try:
        unique_tags = get_unique_tags_cached()
        tag_vector = [0] * len(unique_tags)
        tag_dict = {tag: i for i, tag in enumerate(unique_tags)}

        for tag in tags:
            if tag in tag_dict:
                tag_vector[tag_dict[tag]] = 1

        for tag, data in feedback.items():
            if tag in tag_dict:
                net_feedback = data['positive'] - data['negative']
                if net_feedback >= POSITIVE_THRESHOLD:
                    tag_vector[tag_dict[tag]] = 1

        return tag_vector
    except Exception as e:
        logger.error(f"Error converting tags to vector: {e}", exc_info=True)
        return []


async def training_init(inserted_ids: list[str]) -> None:
    """
    Initializes training for the provided image IDs.

    :param inserted_ids: A list of image document IDs to be processed for training.
    """
    for inserted_id in inserted_ids:
        try:
            image_document = await get_image_document(inserted_id)
            if image_document:
                features = image_document['features'][0]
                feedback_tags = image_document.get('feedback', {})
                tags = image_document['user_tags']
                update_unique_tags_cache()
                tag_vector = tags_to_vector(tags, feedback_tags)
                train_model.delay(features, tag_vector)
                logger.info(f"Training initialized for image: {inserted_id}")
        except Exception as e:
            logger.error(f"Error during training initialization: {e}", exc_info=True)


async def train_init_albums(album_ids: list[str]) -> None:
    """
    Initializes training for the provided album IDs.

    :param album_ids: A list of album IDs to initialize training for.
    """
    for album_id in album_ids:
        try:
            album = await get_album(album_id)
            if not album:
                continue

            image_ids = album.get('images', [])
            await training_init(image_ids)

            sub_album_ids = album.get('sons', [])
            if sub_album_ids:
                await train_init_albums(sub_album_ids)

        except Exception as e:
            logger.error(f"Error while training images in albums: {e}")
            continue


def predictions_to_tag_names(predictions: list[int]) -> list[str]:
    """
    Converts a list of prediction indices to corresponding tag names.

    :param predictions: A list of integers representing prediction indices.
    :return: A list of tag names corresponding to the prediction indices.
    """
    all_tags = get_unique_tags()
    index_to_tag = {i: tag for i, tag in enumerate(all_tags)}
    return [index_to_tag[idx] for idx in predictions if idx in index_to_tag and index_to_tag[idx] != 'NULL']


@shared_task(name=TRAIN_MODEL_TASK, queue=MAIN_QUEUE)
def train_model(features: list[float], tag_vector: list[int]) -> None:
    """
    Trains the model with the provided features and tag vector.

    :param features: A list of feature values for the model.
    :param tag_vector: A list of integers representing the tag vector.
    """
    logger.info("Model training started")
    tag_predictor = update_model_tags(tag_vector)
    if not tag_predictor:
        logger.error("Model not found. Training aborted")
        return

    if not features or not tag_vector:
        logger.error("Features or tag vector not found. Training aborted")
        return

    features_tensor = torch.tensor(features, dtype=torch.float32)
    if features_tensor.ndim == 1:
        features_tensor = features_tensor.unsqueeze(0)

    target = torch.tensor([tag_vector], dtype=torch.float32)
    if target.ndim == 1:
        target = target.unsqueeze(0)

    try:
        criterion = torch.nn.BCELoss()
        optimizer = optim.Adam(tag_predictor.parameters(), lr=LEARNING_RATE)
        optimizer.zero_grad()
        predicted_tags = tag_predictor(features_tensor)
        loss = criterion(predicted_tags, target)
        loss.backward()
        optimizer.step()
        logger.info("Model trained and state saved")
    except Exception as e:
        logger.error(f"Error training model: {e}", exc_info=True)

    save_model_state(tag_predictor)


@shared_task(name=PREDICT_TAGS_TASK, queue=MAIN_QUEUE)
def predict_and_update_tags(image_ids: list[str]) -> None:
    """
    Predicts and updates tags for the provided image IDs.

    :param image_ids: A list of image document IDs for which to predict and update tags.
    """
    for image_id in image_ids:
        try:
            image_document = get_image_document_sync(image_id)
            if not image_document:
                logger.error(f"Couldn't retrieve image document: {image_id}")
                continue

            tag_predictor = update_model_tags()
            if not tag_predictor:
                logger.error(f"Model not found. Prediction aborted for image: {image_id}")
                continue

            features = image_document['features'][0]
            features_tensor = torch.tensor(features, dtype=torch.float32)
            if features_tensor.ndim == 1:
                features_tensor = features_tensor.unsqueeze(0)

            predicted_indices = tag_predictor.predict_tags(features_tensor)
            predicted_tags = predictions_to_tag_names(predicted_indices)
            add_auto_tags(image_id, predicted_tags)
            save_model_state(tag_predictor)
        except Exception as e:
            logger.error(f"Error predicting and updating tags for image: {image_id} - {e}", exc_info=True)
            continue


@shared_task(name=PREDICT_ALL_TAGS_TASK, queue=BEAT_QUEUE)
def update_all_auto_tags() -> None:
    """
    Periodically updates all auto-generated tags for the images in the database.
    """
    logger.info("Updating all auto tags")
    update_unique_tags_cache()
    page_size = 100
    last_id = None
    while True:
        try:
            image_ids = get_image_ids_paginated(last_id, page_size)
            if not image_ids:
                break

            predict_and_update_tags.delay(image_ids)

            last_id = image_ids[-1]
        except Exception as e:
            logger.error(f"Error updating all auto tags: {e}", exc_info=True)
            break
