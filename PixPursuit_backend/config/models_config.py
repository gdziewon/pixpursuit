from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from config.logging_config import setup_logging
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

logger = setup_logging(__name__)


def activate_feature_models() -> tuple[models.ResNet, transforms.Compose]:
    """
    Activate and return the pretrained ResNet50 model and its corresponding transforms.

    :return: A tuple of ResNet50 model and its transforms.
    """
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


def activate_face_models() -> tuple[torch.device, MTCNN, InceptionResnetV1]:
    """
    Activate and return the face detection and recognition models.

    :return: A tuple containing the device, MTCNN, and InceptionResnetV1 models.
    """
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    logger.info("Activated pretrained FaceNet model")
    return device, mtcnn, resnet
