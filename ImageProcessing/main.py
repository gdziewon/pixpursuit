import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image, UnidentifiedImageError
from pymongo import MongoClient, errors
import numpy as np
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
db = client.pixpursuit_db
images_collection = db.images
client.server_info()


def process_image(image_path):
    try:
        image = Image.open(image_path)
    except UnidentifiedImageError:
        print(f"Invalid image file: {image_path}")
        return None

    try:
        faces = mtcnn(image)
        if faces is None:
            print(f"No faces detected in the image: {image_path}")
            return None

        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()

        image_record = {
            'path': image_path,
            'embeddings': [emb.tolist() for emb in embeddings]
        }
        return images_collection.insert_one(image_record).inserted_id
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None


path = "C:\\Users\\Erykoo\\Downloads\\jake.jpg"
process_image(path)