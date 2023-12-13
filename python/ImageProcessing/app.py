from flask import Flask, request, jsonify
import setup
from PIL import Image
import asyncio
from image_processing import process_image_async
from save_to_db import save_to_database

app = Flask(__name__)

database_client, images_collection = setup.connect_to_mongodb()
device, mtcnn, resnet = setup.activate_models()


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
        embeddings_list = loop.run_until_complete(asyncio.gather(
            *(process_image_async(image, device, mtcnn, resnet) for image in processed_images)
        ))
    finally:
        loop.close()

    inserted_ids = []
    for image, embeddings in zip(processed_images, embeddings_list):
        inserted_id = save_to_database(images_collection, image, embeddings)
        inserted_ids.append(str(inserted_id))

    return jsonify({'inserted_ids': inserted_ids})


if __name__ == '__main__':
    app.run(debug=True)
