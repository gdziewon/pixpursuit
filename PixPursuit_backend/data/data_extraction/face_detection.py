from config.models_config import activate_face_models
from data.databases.face_operations import insert_many_faces
from PIL import Image
from utils.constants import FACE_DETECTION_THRESHOLD
from config.logging_config import setup_logging
from utils.constants import FACE_SIZE_THRESHOLD
from torchvision import transforms

logger = setup_logging(__name__)

device, mtcnn, resnet = activate_face_models(thresholds=FACE_DETECTION_THRESHOLD)


def get_face_embeddings(image: Image) -> tuple[list[list[float]], list[list[int]], list[str]]:
    try:
        boxes, _ = mtcnn.detect(image)
        if boxes is None:
            logger.info("No faces detected.")
            return [], [], []

        embeddings_list, boxes_list = [], []
        user_faces_list = []
        for box in boxes:
            width = box[2] - box[0]
            height = box[3] - box[1]
            if width * height > FACE_SIZE_THRESHOLD:
                face = image.crop((box[0], box[1], box[2], box[3]))
                face_tensor = transforms.ToTensor()(face).unsqueeze(0).to(device)
                embedding = resnet(face_tensor)
                embedding = embedding.detach().cpu().numpy().flatten().tolist()

                boxes_list.append(box.tolist())
                embeddings_list.append(embedding)
                user_faces_list.append("anon-1")

        if embeddings_list:
            faces_records = [{"face_emb": emb, 'group': ""} for emb in embeddings_list]
            insert_many_faces(faces_records)

        return embeddings_list, boxes_list, user_faces_list
    except Exception as e:
        logger.error(f"Error getting face embeddings: {type(e).__name__}, {e}")
        return [], [], []
