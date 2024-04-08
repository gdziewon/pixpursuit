"""
utils/exceptions.py

Defines custom exceptions and standard HTTP exceptions used throughout the application.
These exceptions cover various failure scenarios, such as authentication errors, data processing issues,
and other operational errors, providing a structured way to handle error reporting and management.
"""

from fastapi import HTTPException, status
from enum import Enum


class StatusCode(Enum):
    """
    Enum for HTTP status codes used in exceptions.
    """
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    FORBIDDEN = status.HTTP_403_FORBIDDEN


def create_exception(status_code: int, detail: str, headers: dict = None) -> HTTPException:
    """
    Factory function to create HTTPException instances with given status code, detail, and headers.

    :param status_code: The HTTP status code for the exception.
    :param detail: A detailed error message.
    :param headers: Optional headers to include in the HTTP response.
    :return: An instance of HTTPException.
    """
    return HTTPException(status_code=status_code, detail=detail, headers=headers)


# Authentication exceptions
credentials_exception = create_exception(StatusCode.UNAUTHORIZED.value, "Could not validate credentials", {"WWW-Authenticate": "Bearer"})
invalid_credentials_exception = create_exception(StatusCode.FORBIDDEN.value, "Incorrect username or password", {"WWW-Authenticate": "Bearer"})
create_token_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to create tokens")
create_user_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to create user")
invalid_token_exception = create_exception(StatusCode.BAD_REQUEST.value, "Invalid token")
verify_email_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to verify email")
send_confirmation_email_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to send confirmation email")

# Album route exceptions
create_album_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to create new album")
add_images_to_album_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add images to album")
delete_album_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to delete albums")
rename_album_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to rename album")
upload_zip_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to upload zip file")

# Content route exceptions
add_tags_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add tags")
no_image_and_album_ids_exception = create_exception(StatusCode.BAD_REQUEST.value, "No image IDs and album IDs provided")
add_feedback_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add feedback")
add_description_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add description")
add_like_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add like")
add_view_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add view")
remove_tags_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to remove tags")
add_names_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to add names to images")

# Image route exceptions
no_images_found_exception = create_exception(StatusCode.NOT_FOUND.value, "No images found")
process_and_save_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to process and save images")
delete_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to delete images")
relocate_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to relocate images")
find_similar_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to find similar images")
invalid_limit_exception = create_exception(StatusCode.BAD_REQUEST.value, "Invalid limit value")
scrape_and_save_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to scrape and save images")
invalid_url_exception = create_exception(StatusCode.BAD_REQUEST.value, "Invalid URL")

# Image scraper exceptions
get_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to get image URLs")
get_soup_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to get soup")
scrape_images_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to scrape images")
prepare_image_files_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to prepare image files")
clean_up_exception = create_exception(StatusCode.INTERNAL_SERVER_ERROR.value, "Failed to clean up")
