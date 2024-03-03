from config.models_config import activate_feature_models
import torch
from celery import shared_task
from databases.celery_database_tools import add_something_to_image
from io import BytesIO
from PIL import Image
from config.logging_config import setup_logging

logger = setup_logging(__name__)

resnet, transform = activate_feature_models()


@shared_task(name='feature_extraction.extract_features.main', queue='main_queue')
def extract_features(image_data: bytes, filename: str) -> None:
    try:
        image = Image.open(BytesIO(image_data))
        image = image.convert("RGB")
        image = transform(image).unsqueeze(0)
        with torch.no_grad():
            features = resnet(image)

        features.numpy()
        features_list = features.tolist() if features is not None else []
        add_something_to_image('features', features_list, filename)
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        return
