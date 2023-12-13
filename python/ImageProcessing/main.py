import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from pymongo import MongoClient, errors
from io import BytesIO
import numpy as np
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

try:
    client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
    db = client.pixpursuit_db
    images_collection = db.images
    client.server_info()
except errors.ServerSelectionTimeoutError as err:
    print("Failed to connect to server: ", err)


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


def process_image(image_path):
    try:
        image = Image.open(image_path)
        original_image = image_to_byte_array(image)
        resized_image = resize_image(image)
    except UnidentifiedImageError:
        print(f"Invalid image file: {image_path}")
        return None

    try:
        faces = mtcnn(resized_image)
        if faces is None:
            print(f"No faces detected in the image: {image_path}")
            return None

        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()

        exif_data = get_exif_data(image_path)

        image_record = {
            'path': image_path,
            'image_data': original_image,
            'embeddings': [emb.tolist() for emb in embeddings],
            'metadata': exif_data
        }
        return images_collection.insert_one(image_record).inserted_id
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None


