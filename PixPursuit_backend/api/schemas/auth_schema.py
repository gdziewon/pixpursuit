"""
api/schemas/auth_schema.py

Defines Pydantic models for authentication-related data, including user registration,
token generation, and user authentication.
"""

from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """
    Schema for user data.

    :param username: The username of the user.
    :param disabled: Optional boolean indicating if the user account is disabled.
    """
    username: str
    disabled: Optional[bool] = None


class Token(BaseModel):
    """
    Schema for authentication token data.

    :param access_token: The JWT access token.
    :param refresh_token: The JWT refresh token.
    :param token_type: The type of token (e.g., bearer).
    :param username: The username associated with the tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str
    username: str


class TokenData(BaseModel):
    """
    Schema for token data.

    :param username: Optional username associated with the token.
    """
    username: Optional[str] = None


class UserRegistration(BaseModel):
    """
    Schema for user registration data.

    :param email: The email address of the user.
    :param password: The password for the user account.
    """
    email: str
    password: str
