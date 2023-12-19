from setup import activate_feature_models
import asyncio
import torch

resnet, transform = activate_feature_models()


def extract_features(image):
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = resnet(image)
    return features.numpy()


async def extract_features_async(image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_features, image)
