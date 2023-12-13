import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from pymongo import MongoClient, errors
import time


def activate_models():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    return device, mtcnn, resnet


def connect_to_mongodb(attempts=5, delay=3):
    for attempt in range(attempts):
        try:
            client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
            db = client.pixpursuit_db
            collection = db.images
            client.server_info()
            return client, collection
        except errors.ServerSelectionTimeoutError as err:
            if attempt < attempts - 1:
                print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect to MongoDB server: ", err)
                return None, None
