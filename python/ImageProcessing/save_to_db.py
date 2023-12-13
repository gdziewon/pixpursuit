from image_processing import resize_image, image_to_byte_array, process_image, get_exif_data
from PIL import Image


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
