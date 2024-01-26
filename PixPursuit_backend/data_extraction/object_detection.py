from config.models_config import activate_object_models
from celery import shared_task
from databases.database_tools import add_something_to_image
from io import BytesIO
from PIL import Image

model = activate_object_models()


@shared_task(name='object_detection.detect_objects')
def detect_objects(image_data, filename):
    image = Image.open(BytesIO(image_data))
    image = image.convert("RGB")
    results = model.predict(source=image)
    detected_objects = []

    if isinstance(results, list) and len(results) > 0:
        result = results[0]
        for box in result.boxes:
            label_index = int(box.cls)
            label = result.names[label_index]
            confidence = float(box.conf)
            if confidence > 0.7:
                detected_objects.append(label)

    detected_objects = list(set(detected_objects))

    add_something_to_image('detected_objects', detected_objects, filename)
