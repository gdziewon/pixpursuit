import torch
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from facenet_pytorch import MTCNN, InceptionResnetV1
from ultralytics import YOLO
import motor.motor_asyncio
import time
import logging
import boto3
import os

logger = logging.getLogger(__name__)


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
    model = YOLO('yolov8n.pt')
    logger.info("Activated pretrained YOLOv8 model")
    return model


def activate_face_models():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    logger.info("Activated pretrained FaceNet model")
    return device, mtcnn, resnet


def connect_to_mongodb(attempts=5, delay=3):
    for attempt in range(attempts):
        try:
            uri = f"mongodb+srv://Minister:{os.environ['SERVERLESS_INSTANCE_PASSWORD']}@serverlessinstance0.wwjfsv6.mongodb.net/?retryWrites=true&w=majority"
            async_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            db = async_client.pixpursuit_db
            images_collection = db.images
            tags_collection = db.tags
            user_collection = db.users
            directories_collection = db.albums
            return images_collection, tags_collection, user_collection, directories_collection
        except Exception as err:
            if attempt < attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to MongoDB server: ", err)
                return None, None, None


def connect_to_space():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='ams3',
                            endpoint_url='https://pixpursuit.ams3.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    return client
