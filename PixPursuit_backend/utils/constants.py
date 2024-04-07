from dotenv import load_dotenv
import os
from utils.dirs import get_generated_dir_path

load_dotenv()

# Auth
SECRET_KEY_AUTH = os.getenv('AUTH_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_TOKEN_EXPIRE_DAYS = 30

# FastMail
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_APP_PASSWORD = os.getenv('MAIL_APP_PASSWORD')
MAIL_FROM = os.getenv('MAIL_USERNAME')
MAIL_FROM_NAME = "PixPursuit"
CONFIRMATION_URL = "http://localhost:3000/verify-email?token="
EMAIL_SUFFIX = '@pk.edu.pl'

# Tag Prediction
MODEL_FILE_PATH = os.path.join(get_generated_dir_path(), 'tag_predictor_state.pth')
LEARNING_RATE = float(os.getenv('LEARNING_RATE', '0.001'))
POSITIVE_THRESHOLD = 2
TAG_PREDICTION_THRESHOLD = 0.75

# yolov8
YOLO_MODEL_PATH = os.path.join(get_generated_dir_path(), 'yolov8n.pt')
OBJECT_DETECTION_THRESHOLD = 0.5

# Utils
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PK_GALLERY_URL = 'http://www.galeria.pk.edu.pl/index.php?album='

# Digital Ocean Space
DO_REGION = 'ams3'
BUCKET_NAME = 'pixpursuit'
DO_SPACE_ENDPOINT = os.getenv('DO_SPACE_ENDPOINT')
DO_SPACE_ACCESS_KEY = os.getenv('DO_SPACE_ACCESS_KEY')
DO_SPACE_SECRET_KEY = os.getenv('DO_SPACE_SECRET_KEY')
IMAGE_URL_PREFIX = f"{DO_SPACE_ENDPOINT}{BUCKET_NAME}/"

# MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')

# Scraper
BASE_URL = "http://www.galeria.pk.edu.pl"

# Similarity
WEIGHTS = {
        'user_tags': 0.4,
        'user_faces': 0.3,
        'album_id': 0.1,
        'auto_faces': 0.1,
        'auto_tags': 0.05,
        'added_by': 0.03
    }

# Face Detection
FACE_DETECTION_THRESHOLD = [0.6, 0.7, 0.7]
FACE_SIZE_THRESHOLD = 4200

# Celery
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
UPDATE_AUTO_TAGS_SCHEDULE = '*/15'
CLUSTER_FACES_SCHEDULE = '*/5'
BEAT_SCHEDULE_FILE_PATH = os.path.join(get_generated_dir_path(), 'celerybeat-schedule')

# Logging
LOG_FILE_PATH = os.path.join(get_generated_dir_path(), 'app.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Metadata
METADATA_KEYS = ['ImageWidth', 'ImageLength', 'DateTime']
