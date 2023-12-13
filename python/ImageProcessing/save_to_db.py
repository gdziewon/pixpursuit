from image_processing import image_to_byte_array, get_exif_data


def save_to_database(collection, image, embeddings):
    try:
        image_byte_arr = image_to_byte_array(image)
        embeddings_list = [emb.tolist() for emb in embeddings] if embeddings is not None else []

        exif_data = get_exif_data(image)

        image_record = {
            'image_data': image_byte_arr,
            'embeddings': embeddings_list,
            'metadata': exif_data
        }

        return collection.insert_one(image_record).inserted_id
    except Exception as e:
        print(f"Error saving to database: {e}")
        return None
