from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS
import asyncio


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


def get_exif_data(image):
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


def process_image(image, device, mtcnn, resnet):
    resized_image = resize_image(image)
    try:
        faces = mtcnn(resized_image)
        if faces is None:
            return None

        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()
        return embeddings

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


async def process_image_async(image, device, mtcnn, resnet):
    loop = asyncio.get_event_loop()

    def sync_process():
        return process_image(image, device, mtcnn, resnet)

    embeddings = await loop.run_in_executor(None, sync_process)
    return embeddings
