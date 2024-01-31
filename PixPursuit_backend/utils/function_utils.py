import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_generated_dir_path():
    current_file_path = os.path.abspath(__file__)
    generated_files_dir = os.path.join(os.path.dirname(current_file_path), '..', 'generated')
    if not os.path.exists(generated_files_dir):
        os.makedirs(generated_files_dir)
    return generated_files_dir
