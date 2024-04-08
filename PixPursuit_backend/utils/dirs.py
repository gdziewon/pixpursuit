"""
utils/dirs.py

Handles directory operations for the application, such as generating temporary directories
for processing and managing the cleanup of these directories after use.
"""

import os
import shutil
import uuid


def get_generated_dir_path() -> str:
    """
    Gets the path to the directory for storing generated files.
    Creates the directory if it does not exist.

    :return: The absolute path to the generated files' directory.
    """
    current_file_path = os.path.abspath(__file__)
    generated_files_dir = os.path.join(os.path.dirname(current_file_path), '..', 'generated')
    # Ensure the directory exists
    if not os.path.exists(generated_files_dir):
        os.makedirs(generated_files_dir)
    return generated_files_dir


def get_tmp_dir_path() -> str:
    """
    Creates a unique temporary directory for processing and returns its path.

    :return: The absolute path to the created temporary directory.
    """
    current_file_path = os.path.abspath(__file__)
    unique_dir = str(uuid.uuid4())
    tmp_dir = os.path.join(os.path.dirname(current_file_path), '..', unique_dir)
    # Ensure the temporary directory exists
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def cleanup_dir(tmp_dir: str) -> None:
    """
    Recursively deletes a directory and all of its contents.

    :param tmp_dir: The directory to clean up.
    """
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)  # Safe removal of the directory
