import torch
import torch.optim as optim
from config.logging_config import setup_logging
import os
from celery import shared_task
from tag_prediction.tag_prediction_model import TagPredictor
from databases.database_tools import get_image_document
from databases.celery_database_tools import get_image_document_sync, get_unique_tags, add_auto_tags, get_image_ids_paginated
from databases.database_tools import get_album
from utils.constants import POSITIVE_THRESHOLD, LEARNING_RATE, MODEL_FILE_PATH

logger = setup_logging(__name__)


def save_model_state(model, file_path=MODEL_FILE_PATH):
    try:
        torch.save({
            'state_dict': model.state_dict(),
            'num_tags': model.num_tags
        }, file_path)
        logger.info("Model state saved")
    except Exception as e:
        logger.error(f"Error saving model state: {e}", exc_info=True)


def load_model_state(file_path=MODEL_FILE_PATH, input_size=1000, hidden_size=512):
    if not os.path.exists(file_path):
        logger.warning(f"Model file {file_path} not found. Initializing a new model.")
        return TagPredictor(input_size, hidden_size, num_tags=1)

    try:
        checkpoint = torch.load(file_path)
        num_tags = checkpoint['num_tags']
        model = TagPredictor(input_size, hidden_size, num_tags)
        model.load_state_dict(checkpoint['state_dict'])
        logger.info("Model state loaded")
    except Exception as e:
        logger.error(f"Error loading model state: {e}", exc_info=True)
        return None

    return model


async def update_model_tags():
    try:
        tag_predictor = load_model_state()
        unique_tags = get_unique_tags()
        num_tags = len(unique_tags)
        if num_tags != tag_predictor.fc3.out_features:
            tag_predictor.update_output_layer(num_tags)
            save_model_state(tag_predictor)
            logger.info(f"Model output layer updated to match the number of unique tags: {num_tags}")
    except Exception as e:
        logger.error(f"Error updating model tags: {e}", exc_info=True)


def tags_to_vector(tags, feedback):
    try:
        unique_tags = get_unique_tags()
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


async def training_init(inserted_ids):
    for inserted_id in inserted_ids:
        try:
            image_document = await get_image_document(inserted_id)
            if image_document:
                features = image_document['features']
                feedback_tags = image_document.get('feedback', {})
                tags = image_document['user_tags']
                tag_vector = tags_to_vector(tags, feedback_tags)
                train_model.delay(features, tag_vector)
                logger.info(f"Training initialized for image: {inserted_id}")
        except Exception as e:
            logger.error(f"Error during training initialization: {e}", exc_info=True)


async def train_init_albums(album_ids):
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


def predictions_to_tag_names(predictions):
    all_tags = get_unique_tags()
    index_to_tag = {i: tag for i, tag in enumerate(all_tags)}
    return [index_to_tag[idx] for idx in predictions if idx in index_to_tag and index_to_tag[idx] != 'NULL']


@shared_task(name='tag_prediction_tools.train_model')
def train_model(features, tag_vector):
    try:
        tag_predictor = load_model_state()
        if not features or not tag_vector or not tag_predictor:
            logger.error("Training aborted due to missing data")
            return

        features_tensor = torch.tensor(features, dtype=torch.float32)
        if features_tensor.ndim == 1:
            features_tensor = features_tensor.unsqueeze(0)

        target = torch.tensor([tag_vector], dtype=torch.float32)
        if target.ndim == 1:
            target = target.unsqueeze(0)

        criterion = torch.nn.BCELoss()
        optimizer = optim.Adam(tag_predictor.parameters(), lr=LEARNING_RATE)

        optimizer.zero_grad()
        predicted_tags = tag_predictor(features_tensor)
        loss = criterion(predicted_tags, target)
        loss.backward()
        optimizer.step()

        save_model_state(tag_predictor)
        logger.info("Model trained and state saved")
    except Exception as e:
        logger.error(f"Error training model: {e}", exc_info=True)


@shared_task(name='tag_prediction_tools.predict_and_update_tags')
def predict_and_update_tags(image_ids):
    tag_predictor = load_model_state()
    if not tag_predictor:
        logger.error("Model loading failed, prediction aborted.")
        return

    for image_id in image_ids:
        try:
            image_document = get_image_document_sync(image_id)
            if not image_document:
                logger.error(f"Couldn't retrieve image document: {image_id}")
                continue

            features = image_document['features']
            if not features:
                continue

            features_tensor = torch.tensor(features, dtype=torch.float32)
            if features_tensor.ndim == 1:
                features_tensor = features_tensor.unsqueeze(0)
                features_tensor = features_tensor.unsqueeze(-1).unsqueeze(-1)
            elif features_tensor.ndim == 2:
                features_tensor = features_tensor.unsqueeze(1)

            predicted_indices = tag_predictor.predict_tags(features_tensor)
            predicted_tags = predictions_to_tag_names(predicted_indices)
            add_auto_tags(image_id, predicted_tags)
        except Exception as e:
            logger.error(f"Error predicting and updating tags for image: {image_id} - {e}", exc_info=True)
            continue


@shared_task(name='tag_prediction_tools.update_all_auto_tags')
def update_all_auto_tags():
    logger.info("Updating all auto tags")
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
