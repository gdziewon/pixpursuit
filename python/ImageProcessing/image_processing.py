from image_to_byte_array_transformation import image_to_byte_array_async
from metadata_extraction import get_exif_data_async
from face_detection import get_embeddings_async
from object_detection import detect_objects_async


async def process_image_async(image):
    face_embeddings = await get_embeddings_async(image)
    detected_objects = await detect_objects_async(image)
    image_byte_arr = await image_to_byte_array_async(image)
    exif_data = await get_exif_data_async(image)

    return face_embeddings, detected_objects, image_byte_arr, exif_data
