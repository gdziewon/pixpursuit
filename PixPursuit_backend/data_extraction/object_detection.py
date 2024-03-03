from config.models_config import activate_object_models
from celery import shared_task
from databases.celery_database_tools import add_something_to_image
from io import BytesIO
from PIL import Image
from utils.constants import OBJECT_DETECTION_THRESHOLD
from config.logging_config import setup_logging

logger = setup_logging(__name__)

model = activate_object_models()


@shared_task(name='object_detection.detect_objects.main', queue='main_queue')
def detect_objects(image_data: bytes, filename: str) -> None:
    try:
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
                if confidence > OBJECT_DETECTION_THRESHOLD:
                    detected_objects.append(label)

        detected_objects = list(set(detected_objects))

        add_something_to_image('detected_objects', detected_objects, filename)
    except Exception as e:
        logger.error(f"Error detecting objects: {e}")
        return
