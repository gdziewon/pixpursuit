import torch
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from facenet_pytorch import MTCNN, InceptionResnetV1
from ultralytics import YOLO
import motor.motor_asyncio
import time
from logging_config import setup_logging
import boto3
import os
from pymongo.mongo_client import MongoClient

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
            uri = f"mongodb+srv://Minister:{os.environ['SERVERLESS_INSTANCE_PASSWORD']}@cluster0.zt7ht.mongodb.net/?retryWrites=true&w=majority"
            async_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            sync_client = MongoClient(uri)
            async_db = async_client.pixpursuit_db
            sync_db = sync_client.pixpursuit_db
            sync_images_collection = sync_db.images
            async_images_collection = async_db.images
            sync_tags_collection = sync_db.tags
            async_tags_collection = async_db.tags
            user_collection = async_db.users
            directories_collection = async_db.albums
            logger.info("Successfully connected to MongoDB server")
            return async_images_collection, sync_images_collection, async_tags_collection, sync_tags_collection, user_collection, directories_collection
        except Exception as err:
            if attempt < attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to MongoDB server: ", err)
                return None, None, None, None, None


def connect_to_space():
    try:
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name='ams3',
                                endpoint_url='https://pixpursuit.ams3.digitaloceanspaces.com',
                                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    except Exception as e:
        logger.error(f"Failed to connect to Digital Ocean Space: {e}")
        return None
    return client
