"""
data/data_extraction/features_extraction.py

Responsible for extracting feature vectors from images using a pre-trained ResNet model. These feature
vectors are used for various purposes, such as similarity comparison, classification, and indexing.
"""

from config.models_config import activate_feature_models
import torch
from PIL import Image
from config.logging_config import setup_logging

logger = setup_logging(__name__)

resnet, transform = activate_feature_models()


def extract_features(image: Image) -> list[float] or None:
    """
    Extract features from an image using a pre-trained ResNet model.

    :param image: The image to process.
    :return: A list of feature values extracted from the image, or None if an error occurs.
    """
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
