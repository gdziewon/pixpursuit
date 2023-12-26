from image_to_space import image_to_space_async
from metadata_extraction import get_exif_data_async
from face_detection import get_embeddings_async
from object_detection import detect_objects_async
from feature_extraction import extract_features_async
from PIL import Image
from fastapi import UploadFile
from io import BytesIO


async def read_image(file: UploadFile) -> Image:
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    return image


async def process_image_async(upload_file: UploadFile):
    try:
        image = await read_image(upload_file)
        face_embeddings = await get_embeddings_async(image)
        detected_objects = await detect_objects_async(image)
        features = await extract_features_async(image)
        image_url, thumbnail_url = await image_to_space_async(image)
        exif_data = await get_exif_data_async(image)
    except RuntimeError as e:
        print(f"Runtime error occurred: {e}")
        return

    return face_embeddings, detected_objects, image_url, thumbnail_url, exif_data, features
