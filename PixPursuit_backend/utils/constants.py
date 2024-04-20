"""
utils/constants.py

This module contains configuration constants and settings used throughout the application.
These include authentication parameters, email settings, model paths, thresholds, and more.
"""

from dotenv import load_dotenv
import os
from utils.dirs import get_generated_dir_path

load_dotenv()

# Authentication
SECRET_KEY_AUTH = os.getenv('AUTH_SECRET_KEY')  # Secret key for authentication.
ALGORITHM = "HS256"  # Algorithm used for token encoding.
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Access token expiration time in minutes.
REFRESH_TOKEN_EXPIRE_DAYS = 30  # Refresh token expiration time in days.

# Email settings for FastMail
MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Username for mail server.
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Password for mail server.
MAIL_APP_PASSWORD = os.getenv('MAIL_APP_PASSWORD')  # Application-specific password for mail server.
MAIL_FROM = os.getenv('MAIL_USERNAME')  # Email sender address.
MAIL_FROM_NAME = "PixPursuit"  # Name of the email sender.
CONFIRMATION_URL = "http://localhost:3000/verify-email?token="  # URL for email confirmation.
EMAIL_SUFFIX = '@pk.edu.pl'  # Suffix for email addresses.
EMAIL_SUBJECT = "PixPursuit - Email Confirmation"  # Subject line for confirmation emails.
EMAIL_BODY_TEMPLATE = (
    "Please confirm your email by clicking on this link:\n\n{confirmation_url}\n\n"
    "If you did not register to PixPursuit, please ignore this email."
)  # Template for confirmation email body.
EMAIL_SUBTYPE = "html"  # Subtype of the email content.

# Tag Prediction
MODEL_FILE_PATH = os.path.join(get_generated_dir_path(), 'tag_predictor_state.pth')  # File path for saving model state.
LEARNING_RATE = float(os.getenv('LEARNING_RATE', '0.001'))  # Learning rate for model training.
POSITIVE_THRESHOLD = 2  # Threshold for considering a feedback as positive.
TAG_PREDICTION_THRESHOLD = 0.75  # Threshold for tag prediction confidence.

# Utils
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Set of allowed file extensions for images.
PK_GALLERY_URL = 'http://www.galeria.pk.edu.pl/index.php?album='  # Base URL for the gallery.

# Digital Ocean Space configuration
DO_REGION = 'ams3'  # Digital Ocean region.
BUCKET_NAME = 'pixpursuit'  # Name of the Digital Ocean bucket.
DO_SPACE_ENDPOINT = os.getenv('DO_SPACE_ENDPOINT')  # Endpoint for Digital Ocean space.
DO_SPACE_ACCESS_KEY = os.getenv('DO_SPACE_ACCESS_KEY')  # Access key for Digital Ocean space.
DO_SPACE_SECRET_KEY = os.getenv('DO_SPACE_SECRET_KEY')  # Secret key for Digital Ocean space.
IMAGE_URL_PREFIX = f"{DO_SPACE_ENDPOINT}{BUCKET_NAME}/"  # Prefix for image URLs in the space.


# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI')  # URI for MongoDB connection.

# Scraper settings
BASE_URL = "http://www.galeria.pk.edu.pl"  # Base URL for the web scraper.

# Similarity weights for image comparison
WEIGHTS = {
        'features': 0.5,
        'user_tags': 0.4,
        'user_faces': 0.3,
        'album_id': 0.1,
        'auto_faces': 0.1,
        'auto_tags': 0.05,
        'added_by': 0.03
    }  # Weights for factors in image similarity scoring.

# Face Detection
MIN_FACE_SIZE = 3  # Minimum size for a detected face.
FACE_SIZE_THRESHOLD = 4200  # Size threshold for considering a detected face.
FACE_DELETE_THRESHOLD = 0.1  # Threshold for deleting faces.
DBSCAN_EPS = 0.8  # Epsilon value for DBSCAN clustering.
DBSCAN_MIN_SAMPLES = 5  # Minimum samples for DBSCAN clustering.

# Celery configuration
CELERY_BROKER_URL = 'redis://redis:6379/0'  # Broker URL for Celery.
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'  # Backend URL for Celery results.
UPDATE_AUTO_TAGS_SCHEDULE = '*/6'  # Schedule for updating auto tags.
CLUSTER_FACES_SCHEDULE = '*/3'  # Schedule for clustering faces.
BEAT_SCHEDULE_FILE_PATH = os.path.join(get_generated_dir_path(), 'celerybeat-schedule')  # Path for Celery beat schedule file.

# Celery tasks info
MAIN_QUEUE = "main_queue"
BEAT_QUEUE = 'beat_queue'
SHAREPOINT_TASK = "sharepoint_client.initiate_album_processing.main"
EXTRACT_DATA_TASK = "image_processing.extract_data.main"
TRAIN_MODEL_TASK = 'tag_prediction_tools.train_model.main'
PREDICT_TAGS_TASK = 'tag_prediction_tools.predict_and_update_tags.main'
PREDICT_ALL_TAGS_TASK = 'tag_prediction_tools.update_all_auto_tags.beat'
GROUP_FACES_TASK = 'face_operations.group_faces.beat'
UPDATE_NAMES_TASK = 'face_operations.update_names.main'
DELETE_FACES_TASK = 'face_operations.delete_faces_associated_with_images.main'

# Logging configuration
LOG_FILE_PATH = os.path.join(get_generated_dir_path(), 'app.log')  # Path for the log file.
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Format for log messages.

# Metadata keys to extract from images
METADATA_KEYS = ['ImageWidth', 'ImageLength', 'DateTime']  # Keys for metadata extraction.

# Chromedriver settings for Selenium
USER_AGENT_ARG = 'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'  # User agent for Selenium.
HEADLESS_ARG = "--headless"  # Headless argument for Selenium.
DISABLE_GPU_ARG = "--disable-gpu"  # Disable gpu argument for Selenium.
NO_SANDBOX_ARG = "--no-sandbox"  # No sandbox argument for Selenium.
DISABLE_DEV_SHM_USAGE_ARG = "--disable-dev-shm-usage"  # Disable dev shm usage argument for Selenium.
REMOTE_DEBUGGING_PORT_ARG = "--remote-debugging-port=9222"  # Remote debugging port argument for Selenium.
DISABLE_SOFTWARE_RASTERIZER_ARG = "--disable-software-rasterizer"  # Disable software rasterizer argument for Selenium.
DISABLE_EXTENSIONS_ARG = "--disable-extensions"  # Disable extensions argument for Selenium.
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # Path to chromedriver.
HUB_URL = "http://selenium-chrome:4444/wd/hub"  # URL for Selenium hub.

# Selenium fields for logging in.
LOGIN_FIELD = "loginfmt"
USERNAME_FIELD = "UserName"
PASSWORD_FIELD = "Password"
SUBMIT_BUTTON_FIELD = "submitButton"
ACCEPT_BUTTON_FIELD = "idSIButton9"
SP_AUTH_COOKIES = ['FedAuth', 'rtFa']  # Authentication cookies' keys for sharepoint.

# Sharepoint API configuration
API_URL = "/_api/web/GetFolderByServerRelativeUrl('{folder_path}')?$expand=Folders,Files"  # API URL format for Sharepoint.
SHAREPOINT_FETCH_HEADERS = {"Accept": "application/json;odata=verbose"}  # Headers for sharepoint fetch request.

