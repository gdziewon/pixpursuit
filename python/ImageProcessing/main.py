import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from pymongo import MongoClient, errors
from io import BytesIO
import time
import numpy as np
import os


def setup():
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


def resize_image(image, max_size=1200):
    ratio = max_size / max(image.width, image.height)
    if ratio < 1:
        image = image.resize((int(image.width * ratio), int(image.height * ratio)))
    return image


def image_to_byte_array(image: Image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()

    if exif_data:
        formatted_exif_data = {}
        for key, value in exif_data.items():
            if isinstance(value, bytes):
                value = value.decode(errors='ignore')
            elif not isinstance(value, (int, float, str, list, dict, tuple)):
                value = str(value)
            formatted_exif_data[TAGS.get(key, key)] = value
        return formatted_exif_data
    return {}


def process_image(resized_image, device, mtcnn, resnet):
    try:
        faces = mtcnn(resized_image)
        if faces is None:
            print(f"No faces detected in the image")
            return None

        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()
        return embeddings

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def save_to_database(collection, image_path, device, mtcnn, resnet):
    try:
        image = Image.open(image_path)
        resized_image = resize_image(image)
        image_byte_arr = image_to_byte_array(image)

        embeddings = process_image(resized_image, device, mtcnn, resnet)
        embeddings_list = [emb.tolist() for emb in embeddings] if embeddings is not None else []

        exif_data = get_exif_data(image_path)

        image_record = {
            'path': image_path,
            'image_data': image_byte_arr,
            'embeddings': embeddings_list,
            'metadata': exif_data
        }

        return collection.insert_one(image_record).inserted_id
    except Exception as e:
        print(f"Error saving to database: {e}")
        return None


database_client, images_collection = connect_to_mongodb()
g_device, g_mtcnn, g_resnet = setup()

