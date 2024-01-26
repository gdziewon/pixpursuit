from config.models_config import activate_face_models
from celery import shared_task
from databases.database_tools import add_something_to_image
from databases.face_operations import insert_many_faces
from io import BytesIO
from PIL import Image

device, mtcnn, resnet = activate_face_models()


@shared_task(name='face_detection.get_face_embeddings')
def get_face_embeddings(image_data, filename):
    image = Image.open(BytesIO(image_data))
    image = image.convert("RGB")
    try:
        boxes, _ = mtcnn.detect(image)
        if boxes is None:
            return None, None

        faces = mtcnn(image)
        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()

        boxes_list = [box.tolist() for box in boxes] if boxes is not None else []
        embeddings_list = [emb.tolist() for emb in embeddings] if embeddings is not None else []

        user_faces_list = [f"anon{i}" for i in range(len(embeddings_list))]

        add_something_to_image('embeddings', embeddings_list, filename)
        add_something_to_image('embeddings_box', boxes_list, filename)
        add_something_to_image('user_faces',  user_faces_list, filename)

        faces_records = [{"face_emb": emb, 'group': ""} for emb in embeddings_list]
        insert_many_faces(faces_records)

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None
