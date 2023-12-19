from flask import Flask, request, jsonify
from PIL import Image
import asyncio
from image_processing import process_image_async
from database_tools import save_to_database, add_tags, add_feedback, predict_and_update_tags
from tag_prediction_model import TagPredictor
from tag_prediction_tools import update_model_tags, added_tag_training_init, feedback_training_init, save_model_state
from celery_config import celery
import numpy as np
from error_handling import allowed_file

tag_predictor = TagPredictor(input_size=1000, hidden_size=512, num_tags=1)
save_model_state(tag_predictor)

app = Flask(__name__)
celery.conf.update(app.config)


@app.route('/process-images', methods=['POST'])
def process_images_api():
    image_files = request.files.getlist('image')

    if not image_files:
        return jsonify({'error': 'No images provided'}), 400

    processed_images = []
    for image_file in image_files:
        if image_file.filename:
            if not allowed_file(image_file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            image = Image.open(image_file.stream)
            processed_images.append(image)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(asyncio.gather(
            *(process_image_async(image) for image in processed_images)
        ))

        inserted_ids = []
        for (face_embeddings, detected_objects, image_byte_arr, exif_data, features) in results:
            inserted_id = save_to_database(face_embeddings, detected_objects, image_byte_arr, exif_data, features)
            inserted_id_str = str(inserted_id)
            features_list = features.tolist() if isinstance(features, np.ndarray) else features
            predict_and_update_tags.delay(inserted_id_str, features_list)

            inserted_ids.append(inserted_id_str)
    finally:
        loop.close()

    return jsonify({'inserted_ids': inserted_ids})


@app.route('/add-user-tag', methods=['POST'])
def add_user_tag_api():
    try:
        data = request.get_json()
        inserted_id = data['inserted_id']
        tags = data['tags']

        success = add_tags(tags, inserted_id)
        if success:
            update_model_tags(tag_predictor)
            added_tag_training_init(inserted_id)
            return jsonify({'message': 'Tags added successfully'}), 200
        else:
            return jsonify({'error': 'Failed to add tags'}), 500
    except Exception as e:
        print(f"Error in /add-user-tag: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/feedback-on-tags', methods=['POST'])
def feedback_on_tags_api():
    data = request.get_json()
    inserted_id = data.get('inserted_id')
    feedback = data.get('feedback')

    if not inserted_id or feedback is None:
        return jsonify({'error': 'Missing inserted_id or feedback'}), 400

    success = add_feedback(feedback, inserted_id)
    if success:
        feedback_training_init(inserted_id)
        return jsonify({'message': 'Feedback added successfully'}), 200
    else:
        return jsonify({'error': 'Failed to add feedback'}), 500


if __name__ == '__main__':
    app.run(debug=True)
