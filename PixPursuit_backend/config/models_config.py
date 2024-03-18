from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from ultralytics import YOLO
from config.logging_config import setup_logging
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from utils.constants import YOLO_MODEL_PATH, FACE_DETECTION_THRESHOLD

logger = setup_logging(__name__)


def activate_feature_models() -> (models.ResNet, transforms.Compose):
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


def activate_object_models() -> YOLO:
    model = YOLO(YOLO_MODEL_PATH)
    logger.info("Activated pretrained YOLOv8 model")
    return model


def activate_face_models(thresholds=FACE_DETECTION_THRESHOLD) -> (torch.device, MTCNN, InceptionResnetV1):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, thresholds=thresholds, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    logger.info("Activated pretrained FaceNet model")
    return device, mtcnn, resnet
