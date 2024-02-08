from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from ultralytics import YOLO
from config.logging_config import setup_logging
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import os
from utils.function_utils import get_generated_dir_path

logger = setup_logging(__name__)


def activate_feature_models():
    weights = ResNet50_Weights.DEFAULT
    resnet = models.resnet50(weights=weights)
    resnet.eval()

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    logger.info("Activated pretrained ResNet50 model")
    return resnet, transform


def activate_object_models():
    model_path = os.path.join(get_generated_dir_path(), 'yolov8n.pt')
    model = YOLO(model_path)
    logger.info("Activated pretrained YOLOv8 model")
    return model


def activate_face_models(thresholds=[0.6, 0.7, 0.7]):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, thresholds=thresholds, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    logger.info("Activated pretrained FaceNet model")
    return device, mtcnn, resnet
