"""
services/authentication/auth.py

Provides authentication functionalities for the application, including user authentication,
password verification, token creation, and retrieval of current user information based on tokens.
Utilizes JWT for token management and Argon2 for password hashing.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from data.databases.mongodb.async_db.database_tools import get_user
from argon2 import PasswordHasher
import argon2.exceptions
from config.logging_config import setup_logging
from api.schemas.auth_schema import TokenData, User
from utils.constants import SECRET_KEY_AUTH, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from utils.exceptions import credentials_exception, invalid_credentials_exception, create_token_exception

logger = setup_logging(__name__)

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the given plain password matches the hashed password using Argon2.

    :param plain_password: The plain text password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the passwords match, False otherwise.
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False


async def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticates a user by verifying their username and password.

    :param username: The username of the user to authenticate.
    :param password: The password of the user to authenticate.
    :return: The user's data if authentication is successful.
    :raises invalid_credentials_exception: If authentication fails.
    """
    user = await get_user(username)
    if not user or not user['verified']:
        raise invalid_credentials_exception

    try:
        valid_password = await verify_password(password, user['password'])
    except argon2.exceptions.InvalidHashError:
        logger.error(f"Invalid hash for user {username}")
        valid_password = False
    if not valid_password:
        raise invalid_credentials_exception
    return user


def create_token(data: dict, expires_delta: timedelta = 30) -> str or None:
    """
    Creates a JWT token with the specified data and expiration time.

    :param data: The data to encode in the token.
    :param expires_delta: The time delta for token expiration.
    :return: The encoded JWT token, or None if token creation fails.
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY_AUTH, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create token: {str(e)}")
        return None


def get_tokens(username: str) -> tuple[str, str] or None:
    """
    Generates access and refresh tokens for the given username.

    :param username: The username for which to create the tokens.
    :return: A tuple containing the access token and the refresh token.
    :raises create_token_exception: If token creation fails.
    """
    try:
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_token(
            data={"sub": username,
                  "type": "access"},
            expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_token(
            data={"sub": username,
                  "type": "refresh"},
            expires_delta=refresh_token_expires
        )
        return access_token, refresh_token
    except Exception as e:
        logger.error(f"Failed to create tokens: {str(e)}")
        raise create_token_exception


async def decode_token(token: str, expected_type: str) -> User or None:
    """
    Decodes the JWT token and retrieves the user if the token type matches the expected type.

    :param token: The JWT token to decode.
    :param expected_type: The expected token type (e.g., 'access' or 'refresh').
    :return: The User model of the authenticated user.
    :raises credentials_exception: If token is invalid, type does not match, or user does not exist.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if username is None or token_type != expected_type:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(**user)


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> User or None:
    """
    Retrieves the current user based on the provided access token.

    :param request: The request object.
    :param token: The JWT access token.
    :return: The User model of the authenticated user.
    :raises credentials_exception: If token is invalid or user does not exist.
    """
    user_model = await decode_token(token, "access")
    if user_model is not None:
        request.state.username = user_model.username
    return user_model


async def get_current_user_refresh(token: str = Depends(oauth2_scheme)) -> User or None:
    """
    Retrieves the current user based on the provided refresh token.

    :param token: The JWT refresh token.
    :return: The User model of the authenticated user.
    :raises credentials_exception: If token is invalid or user does not exist.
    """
    return await decode_token(token, "refresh")
