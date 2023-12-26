from setup import activate_object_models
import asyncio

model = activate_object_models()


def detect_objects(image):
    results = model.predict(source=image)
    detected_objects = []

    if isinstance(results, list) and len(results) > 0:
        result = results[0]

        for box in result.boxes:
            label_index = int(box.cls)
            label = result.names[label_index]
            confidence = float(box.conf)
            if confidence > 0.7:
                detected_objects.append({'name': label, 'confidence': confidence})

    return detected_objects


async def detect_objects_async(image):
    return await asyncio.to_thread(detect_objects, image)
