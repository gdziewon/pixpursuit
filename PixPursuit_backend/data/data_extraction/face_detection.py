"""
data/data_extraction/face_detection.py

Handles the detection and processing of faces within images. This includes detecting face locations,
extracting embeddings, and filtering based on size thresholds. Utilizes a pre-trained model for face
detection and embedding extraction.
"""

from config.models_config import activate_face_models
from data.databases.mongodb.sync_db.face_operations import insert_many_faces
from PIL import Image
from utils.constants import FACE_DETECTION_THRESHOLD, FACE_SIZE_THRESHOLD
from config.logging_config import setup_logging
from torchvision import transforms

logger = setup_logging(__name__)

device, mtcnn, resnet = activate_face_models(thresholds=FACE_DETECTION_THRESHOLD)


def detect_faces(image: Image) -> list:
    """
    Detect faces in an image.

    :param image: The image to detect faces in.
    :return: Bounding boxes of detected faces, if any.
    """
    boxes, _ = mtcnn.detect(image)
    return boxes


def process_face(image: Image, box: list) -> tuple[list, list]:
    """
    Process a detected face to get its embedding.

    :param image: The image containing the face.
    :param box: The bounding box of the face.
    :return: The embedding of the face and its bounding box.
    """
    face = image.crop((box[0], box[1], box[2], box[3]))
    face_tensor = transforms.ToTensor()(face).unsqueeze(0).to(device)
    embedding = resnet(face_tensor)
    embedding = embedding.detach().cpu().numpy().flatten().tolist()
    return embedding, box


def get_face_embeddings(image: Image) -> tuple[list[list[float]], list[list[int]], list[str]]:
    """
    Get embeddings for all faces in an image.

    :param image: The image to process.
    :return: A tuple containing lists of embeddings, bounding boxes, and face identifiers.
    """
    try:
        boxes = detect_faces(image)
        if boxes is None:
            logger.info("No faces detected.")
            return [], [], []

        embeddings_list, boxes_list, user_faces_list = [], [], []
        for box in boxes:
            width = box[2] - box[0]  # Calculate face width
            height = box[3] - box[1]  # Calculate face height
            if width * height > FACE_SIZE_THRESHOLD:  # Check if face is larger than the threshold
                embedding, processed_box = process_face(image, box)
                embeddings_list.append(embedding)
                boxes_list.append(processed_box)
                user_faces_list.append("anon-1")  # Assign a default anonymous ID

        if embeddings_list:
            # Create records to insert into the database
            faces_records = [{"face_emb": emb, 'group': ""} for emb in embeddings_list]
            insert_many_faces(faces_records)

        return embeddings_list, boxes_list, user_faces_list
    except Exception as e:
        logger.error(f"Error getting face embeddings: {type(e).__name__}, {e}")
        return [], [], []

