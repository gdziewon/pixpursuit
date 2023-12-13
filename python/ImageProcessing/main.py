import setup
from save_to_db import save_to_database

database_client, images_collection = setup.connect_to_mongodb()
device, mtcnn, resnet = setup.activate_models()
path = "C:\\Users\\Erykoo\\Downloads\\eryk.jpg"
save_to_database(images_collection, path, device, mtcnn, resnet)
