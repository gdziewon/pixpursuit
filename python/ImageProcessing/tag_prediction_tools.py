import torch
import torch.optim as optim
from bson import ObjectId
from celery_config import celery
import logging
import os

logger = logging.getLogger(__name__)

MODEL_FILE_PATH = os.getenv('MODEL_FILE_PATH', 'tag_predictor_state.pth')
LEARNING_RATE = float(os.getenv('LEARNING_RATE', '0.001'))


def save_model_state(model, file_path=MODEL_FILE_PATH):
    try:
        torch.save(model.state_dict(), file_path)
        logger.info(f"Model state saved")
    except Exception as e:
        logger.error(f"Error saving model state {e}", exc_info=True)


def load_model_state(file_path=MODEL_FILE_PATH, input_size=2048, hidden_size=1024, num_tags=100):
    try:
        from tag_prediction_model import TagPredictor
        model = TagPredictor(input_size, hidden_size, num_tags)
        model.load_state_dict(torch.load(file_path))
        logger.info(f"Model state loaded")
        return model
    except Exception as e:
        logger.error(f"Error loading model state {e}", exc_info=True)
        return None


def added_tag_training_init(inserted_id):
    try:
        from database_tools import get_image_document
        inserted_id = ObjectId(inserted_id)
        image_document = get_image_document(inserted_id)
        if image_document:
            features = image_document['features']
            user_tags = image_document.get('user_tags', [])
            tag_vector = tags_to_vector(user_tags, {})
            train_model.delay(features, tag_vector)
            logger.info(f"Training initialized for added tags {user_tags} for ID {inserted_id}")
    except Exception as e:
        logger.error(f"Error during added tag training initialization {e}", exc_info=True)


def feedback_training_init(inserted_id):
    try:
        from database_tools import get_image_document
        inserted_id = ObjectId(inserted_id)
        image_document = get_image_document(inserted_id)
        if image_document:
            features = image_document['features']
            feedback_tags = image_document.get('feedback', {})
            tags = image_document['user_tags']
            feedback_vector = tags_to_vector(tags, feedback=feedback_tags)
            train_model.delay(features, feedback_vector)
            logger.info(f"Training initialized for feedback {feedback_tags} on tags for ID {inserted_id}")
    except Exception as e:
        logger.error(f"Error during feedback training initialization {e}", exc_info=True)


def update_model_tags(tag_predictor):
    try:
        from database_tools import get_unique_tags
        num_tags = len(get_unique_tags())
        if num_tags != tag_predictor.fc3.out_features:
            tag_predictor.update_output_layer(num_tags)
            logger.info(f"Model output layer updated to match the number of unique tags: {num_tags}")
    except Exception as e:
        logger.error(f"Error updating model tags {e}", exc_info=True)


def tags_to_vector(tags, feedback):
    try:
        from database_tools import get_unique_tags
        unique_tags = get_unique_tags()
        tag_vector = [0] * len(unique_tags)
        tag_dict = {tag: i for i, tag in enumerate(unique_tags)}

        for tag in tags:
            if tag in tag_dict:
                tag_vector[tag_dict[tag]] = 1

        for tag, value in feedback.items():
            if tag in tag_dict:
                tag_vector[tag_dict[tag]] = 1 if value else 0

        return tag_vector
    except Exception as e:
        logger.error(f"Error converting tags to vector {e}", exc_info=True)
        return []


@celery.task(name='tag_prediction_tools.train_model')
def train_model(features, tag_vector):
    try:
        model = load_model_state()
        if not model:
            logger.error("Model loading failed, training aborted.")
            return

        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        target = torch.tensor([tag_vector], dtype=torch.float32)

        criterion = torch.nn.BCELoss()
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

        predicted_tags = model(features_tensor)
        loss = criterion(predicted_tags, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        save_model_state(model)
        logger.info("Model trained and state saved")
    except Exception as e:
        logger.error(f"Error during model training {e}", exc_info=True)
