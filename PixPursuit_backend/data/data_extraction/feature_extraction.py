from config.models_config import activate_feature_models
import torch
from PIL import Image
from config.logging_config import setup_logging

logger = setup_logging(__name__)

resnet, transform = activate_feature_models()


def extract_features(image: Image) -> list[float] or None:
    try:
        image = transform(image).unsqueeze(0)
        with torch.no_grad():
            features = resnet(image)

        features.numpy()
        features_list = features.tolist() if features is not None else []

        return features_list
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        return
