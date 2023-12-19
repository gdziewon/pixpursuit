import torch
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from facenet_pytorch import MTCNN, InceptionResnetV1
from ultralytics import YOLO
from pymongo import MongoClient, errors
import time


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
    return resnet, transform


def activate_object_models():
    model = YOLO('yolov8n.pt')
    return model


def activate_face_models():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    return device, mtcnn, resnet


def connect_to_mongodb(attempts=5, delay=3):
    for attempt in range(attempts):
        try:
            client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
            db = client.pixpursuit_db
            images_collection = db.images
            tags_collection = db.tags
            client.server_info()
            return client, images_collection, tags_collection
        except errors.ServerSelectionTimeoutError as err:
            if attempt < attempts - 1:
                print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect to MongoDB server: ", err)
                return None, None
