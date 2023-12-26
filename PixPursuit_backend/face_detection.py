from setup import activate_face_models
import asyncio

device, mtcnn, resnet = activate_face_models()


def resize_image(image, max_size=1200):
    ratio = max_size / max(image.width, image.height)
    if ratio < 1:
        image = image.resize((int(image.width * ratio), int(image.height * ratio)))
    return image


def get_face_embeddings(image):
    resized_image = resize_image(image)
    try:
        faces = mtcnn(resized_image)
        if faces is None:
            return None

        embeddings = resnet(faces.to(device))
        embeddings = embeddings.detach().cpu().numpy()
        return embeddings

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


async def get_embeddings_async(image):
    loop = asyncio.get_event_loop()

    def sync_process():
        return get_face_embeddings(image)

    embeddings = await loop.run_in_executor(None, sync_process)
    return embeddings
