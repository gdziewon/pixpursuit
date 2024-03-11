from config.models_config import activate_face_models
from celery import shared_task
from databases.celery_database_tools import add_something_to_image
from databases.face_operations import insert_many_faces
from io import BytesIO
from PIL import Image
from utils.constants import FACE_DETECTION_THRESHOLD
from config.logging_config import setup_logging
from utils.constants import FACE_SIZE_THRESHOLD
logger = setup_logging(__name__)

device, mtcnn, resnet = activate_face_models(thresholds=FACE_DETECTION_THRESHOLD)


@shared_task(name='face_detection.get_face_embeddings.main', queue='main_queue')
def get_face_embeddings(image_data: bytes, filename: str) -> None:
    image = Image.open(BytesIO(image_data))
    image = image.convert("RGB")
    try:
        boxes, _ = mtcnn.detect(image)
        if boxes is None:
            return None

        faces = mtcnn(image)
        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()

        boxes_list = []
        embeddings_list = []
        for i in range(len(boxes)):
            box = boxes[i]
            width = box[2] - box[0]
            height = box[3] - box[1]
            if width * height > FACE_SIZE_THRESHOLD:
                boxes_list.append(box.tolist())
                embeddings_list.append(embeddings[i].tolist())

        user_faces_list = ["anon-1" for _ in range(len(embeddings_list))]

        add_something_to_image('embeddings', embeddings_list, filename)
        add_something_to_image('embeddings_box', boxes_list, filename)
        add_something_to_image('user_faces',  user_faces_list, filename)
        add_something_to_image('backlog_faces', user_faces_list, filename)

        faces_records = [{"face_emb": emb, 'group': ""} for emb in embeddings_list]
        insert_many_faces(faces_records)

    except Exception as e:
        logger.error(f"Error getting face embeddings: {e}")
        return
