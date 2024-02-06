import os
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def is_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_allowed_url(url):
    return url.startswith('http://www.galeria.pk.edu.pl/index.php?album=')


def get_generated_dir_path():
    current_file_path = os.path.abspath(__file__)
    generated_files_dir = os.path.join(os.path.dirname(current_file_path), '..', 'generated')
    if not os.path.exists(generated_files_dir):
        os.makedirs(generated_files_dir)
    return generated_files_dir


async def get_tmp_dir_path():
    current_file_path = os.path.abspath(__file__)
    unique_dir = str(uuid.uuid4())
    tmp_dir = os.path.join(os.path.dirname(current_file_path), '..', unique_dir)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    return tmp_dir
