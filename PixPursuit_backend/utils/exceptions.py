from fastapi import HTTPException, status
from enum import Enum


class StatusCode(Enum):
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    FORBIDDEN = status.HTTP_403_FORBIDDEN


# Authentication exceptions
credentials_exception = HTTPException(
    status_code=StatusCode.UNAUTHORIZED.value,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"})
invalid_credentials_exception = HTTPException(
    status_code=StatusCode.FORBIDDEN.value,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"})
create_token_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to create tokens")
create_user_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to create user")
invalid_token_exception = HTTPException(
    status_code=StatusCode.BAD_REQUEST.value,
    detail="Invalid token")
verify_email_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to verify email")
send_confirmation_email_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to send confirmation email")

# Album route exceptions
create_album_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to create new album")
add_images_to_album_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add images to album")
delete_album_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to delete albums")
rename_album_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to rename album")

# Content route exceptions
add_tags_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add tags")
no_image_and_album_ids_exception = HTTPException(
    status_code=StatusCode.BAD_REQUEST.value,
    detail="No image IDs and album IDs provided")
add_feedback_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add feedback")
add_description_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add description")
add_like_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add like")
add_view_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add view")
remove_tags_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to remove tags")
add_names_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to add names to images")

# Image route exceptions
no_images_found_exception = HTTPException(
    status_code=StatusCode.NOT_FOUND.value,
    detail="No images found")
process_and_save_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to process and save images")
delete_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to delete images")
relocate_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to relocate images")
find_similar_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to find similar images")
invalid_limit_exception = HTTPException(
    status_code=StatusCode.BAD_REQUEST.value,
    detail="Invalid limit value")
scrape_and_save_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to scrape and save images")
invalid_url_exception = HTTPException(
    status_code=StatusCode.BAD_REQUEST.value,
    detail="Invalid URL")

# Image scraper exceptions
get_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to get image URLs")
get_soup_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to get soup")
scrape_images_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to scrape images")
prepare_image_files_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to prepare image files")
clean_up_exception = HTTPException(
    status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
    detail="Failed to clean up")
