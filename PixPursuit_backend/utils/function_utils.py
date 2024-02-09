from bson import ObjectId
from utils.constants import ALLOWED_EXTENSIONS, PK_GALLERY_URL


def is_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_allowed_url(url):
    return url.startswith(PK_GALLERY_URL)


def to_object_id(id_str):
    try:
        id_obj = ObjectId(id_str)
        return id_obj
    except Exception as e:
        return None
