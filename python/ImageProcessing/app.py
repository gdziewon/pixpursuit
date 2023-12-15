from flask import Flask, request, jsonify
from PIL import Image
import asyncio
from image_processing import process_image_async
from save_to_db import save_to_database

app = Flask(__name__)


@app.route('/process-images', methods=['POST'])
def process_images_api():
    image_files = request.files.getlist('image')

    if not image_files:
        return jsonify({'error': 'No images provided'}), 400

    processed_images = []
    for image_file in image_files:
        if image_file.filename:
            image = Image.open(image_file.stream)
            processed_images.append(image)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(asyncio.gather(
            *(process_image_async(image) for image in processed_images)
        ))
    finally:
        loop.close()

    inserted_ids = []
    for (face_embeddings, detected_objects, image_byte_arr, exif_data) in results:
        inserted_id = save_to_database(face_embeddings, detected_objects, image_byte_arr, exif_data)
        inserted_ids.append(str(inserted_id))

    return jsonify({'inserted_ids': inserted_ids})


if __name__ == '__main__':
    app.run(debug=True)
