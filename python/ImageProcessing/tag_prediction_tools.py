import torch
import torch.optim as optim
from bson import ObjectId
from celery_config import celery


def save_model_state(model, file_path='tag_predictor_state.pth'):
    torch.save(model.state_dict(), file_path)


def load_model_state(file_path='tag_predictor_state.pth', input_size=2048, hidden_size=1024, num_tags=100):
    from tag_prediction_model import TagPredictor
    model = TagPredictor(input_size, hidden_size, num_tags)
    model.load_state_dict(torch.load(file_path))
    return model


def added_tag_training_init(inserted_id):
    from database_tools import get_image_document
    inserted_id = ObjectId(inserted_id)
    image_document = get_image_document(inserted_id)
    if image_document:
        features = image_document['features']
        user_tags = image_document.get('user_tags', [])
        tag_vector = tags_to_vector(user_tags, {})
        train_model.delay(features, tag_vector)


def feedback_training_init(inserted_id):
    from database_tools import get_image_document
    inserted_id = ObjectId(inserted_id)
    image_document = get_image_document(inserted_id)
    if image_document:
        features = image_document['features']
        feedback_tags = image_document.get('feedback', {})
        tags = image_document['user_tags']
        feedback_vector = tags_to_vector(tags, feedback=feedback_tags)
        train_model.delay(features, feedback_vector)


def update_model_tags(tag_predictor):
    from database_tools import get_unique_tags
    num_tags = len(get_unique_tags())
    if num_tags != tag_predictor.fc3.out_features:
        tag_predictor.update_output_layer(num_tags)


def tags_to_vector(tags, feedback):
    from database_tools import get_unique_tags
    unique_tags = get_unique_tags()
    tag_vector = [0] * len(unique_tags)
    tag_dict = {tag: i for i, tag in enumerate(unique_tags)}

    for tag in tags:
        if tag in tag_dict:
            tag_vector[tag_dict[tag]] = 1

    for tag, value in feedback.items():
        if tag in tag_dict:
            tag_vector[tag_dict[tag]] = 1 if value else 0

    return tag_vector


@celery.task(name='tag_prediction_tools.train_model')
def train_model(features, tag_vector):
    model = load_model_state()
    features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    target = torch.tensor([tag_vector], dtype=torch.float32)

    criterion = torch.nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    predicted_tags = model(features_tensor)
    loss = criterion(predicted_tags, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    save_model_state(model)
