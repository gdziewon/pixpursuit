import os
import uuid


def get_generated_dir_path():
    current_file_path = os.path.abspath(__file__)
    generated_files_dir = os.path.join(os.path.dirname(current_file_path), '..', 'generated')
    if not os.path.exists(generated_files_dir):
        os.makedirs(generated_files_dir)
    return generated_files_dir


def get_tmp_dir_path():
    current_file_path = os.path.abspath(__file__)
    unique_dir = str(uuid.uuid4())
    tmp_dir = os.path.join(os.path.dirname(current_file_path), '..', unique_dir)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    return tmp_dir
