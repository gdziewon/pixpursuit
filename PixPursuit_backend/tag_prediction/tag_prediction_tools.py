import torch
import torch.optim as optim
from bson import ObjectId
from config.logging_config import setup_logging
import os
from celery import shared_task
from tag_prediction.tag_prediction_model import TagPredictor
from databases.database_tools import get_image_document, get_image_document_sync, get_unique_tags, add_auto_tags, get_image_ids_paginated
from utils.function_utils import get_generated_dir_path

logger = setup_logging(__name__)

MODEL_FILE_PATH = os.path.join(get_generated_dir_path(), 'tag_predictor_state.pth')
LEARNING_RATE = float(os.getenv('LEARNING_RATE', '0.001'))
POSITIVE_THRESHOLD = 3


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


async def training_init(inserted_id):
    try:
        image_document = await get_image_document(inserted_id)
        if image_document:
            features = image_document['features']
            feedback_tags = image_document.get('feedback', {})
            tags = image_document['user_tags']
            await update_model_tags()
            tag_vector = tags_to_vector(tags, feedback_tags)
            train_model.delay(features, tag_vector)
            logger.info(f"Training initialized for image: {inserted_id}")
    except Exception as e:
        logger.error(f"Error during training initialization: {e}", exc_info=True)


def predictions_to_tag_names(predictions):
    all_tags = get_unique_tags()
    index_to_tag = {i: tag for i, tag in enumerate(all_tags)}
    return [index_to_tag[idx] for idx in predictions if idx in index_to_tag and index_to_tag[idx] != 'NULL']


@shared_task(name='tag_prediction_tools.train_model')
def train_model(features, tag_vector):
    tag_predictor = load_model_state()
    if not features:
        logger.error("Image has no features")
        return

    if not tag_predictor:
        logger.error("Model loading failed, training aborted.")
        return

    logger.info("Model training started")

    features_tensor = torch.tensor(features, dtype=torch.float32)
    if features_tensor.ndim == 1:
        features_tensor = features_tensor.unsqueeze(0)

    target = torch.tensor([tag_vector] if features_tensor.ndim == 1 else tag_vector, dtype=torch.float32)

    if features_tensor.size(0) != target.size(0):
        target = target.unsqueeze(0)

    criterion = torch.nn.BCELoss()
    optimizer = optim.Adam(tag_predictor.parameters(), lr=LEARNING_RATE)

    predicted_tags = tag_predictor(features_tensor)
    loss = criterion(predicted_tags, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    save_model_state(tag_predictor)
    logger.info("Model trained and state saved")


@shared_task(name='tag_prediction_tools.predict_and_update_tags')
def predict_and_update_tags(image_ids):
    logger.info("Predicting and updating tags")
    tag_predictor = load_model_state()
    if not tag_predictor:
        logger.error("Model loading failed, prediction aborted.")
        return

    for image_id in image_ids:
        image_id_obj = ObjectId(image_id)
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

        predicted_indices = tag_predictor.predict_tags(features_tensor)
        predicted_tags = predictions_to_tag_names(predicted_indices)

        add_auto_tags(image_id_obj, predicted_tags)


@shared_task(name='tag_prediction_tools.update_all_auto_tags')
def update_all_auto_tags():
    try:
        logger.info("Updating all auto tags")
        page_number = 1
        page_size = 100
        while True:
            image_ids = get_image_ids_paginated(page_number, page_size)
            if not image_ids:
                break

            predict_and_update_tags.delay(image_ids)

            page_number += 1
    except Exception as e:
        logger.error(f"Error in update_all_auto_tags: {e}")
