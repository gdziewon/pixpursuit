from setup import connect_to_mongodb

database_client, images_collection = connect_to_mongodb()


def save_to_database(face_embeddings, detected_objects, image_byte_arr, exif_data):
    try:
        embeddings_list = [emb.tolist() for emb in face_embeddings] if face_embeddings is not None else []

        image_record = {
            'image_data': image_byte_arr,
            'embeddings': embeddings_list,
            'detected_objects': detected_objects,
            'metadata': exif_data
        }

        return images_collection.insert_one(image_record).inserted_id
    except Exception as e:
        print(f"Error saving to database: {e}")
        return None
