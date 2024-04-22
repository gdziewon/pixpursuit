"""
services/authentication/registration.py

Provides functionalities for hashing passwords, creating confirmation tokens, and sending
email confirmations to users. This module uses the FastAPI-Mail for email operations and
argon2 for password hashing.
"""

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
from argon2 import PasswordHasher
from config.logging_config import setup_logging
from utils.constants import (
    SECRET_KEY_AUTH, ALGORITHM, MAIL_USERNAME, MAIL_APP_PASSWORD,
    MAIL_FROM, MAIL_FROM_NAME, CONFIRMATION_URL, EMAIL_SUBTYPE, EMAIL_BODY_TEMPLATE, EMAIL_SUBJECT
)
from utils.exceptions import send_confirmation_email_exception

logger = setup_logging(__name__)

ph = PasswordHasher()


def get_connection_config() -> ConnectionConfig:
    """
    Returns configuration for FastMail connection

    :return: A ConnectionConfig object
    """
    return ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_APP_PASSWORD,
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_FROM_NAME=MAIL_FROM_NAME,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )


async def hash_password(password: str) -> str:
    """
    Hashes a password using the Argon2 algorithm.

    :param password: The plain text password to hash.
    :return: The hashed password.
    """
    return ph.hash(password)


def create_confirmation_token(user_id: str) -> str:
    """
    Creates a JWT token to be used in email confirmation.

    :param user_id: The user ID to include in the token.
    :return: A JWT token for confirming the user's email address.
    """
    payload = {"user_id": str(user_id)}  # Convert ObjectId to string
    token = jwt.encode(payload, SECRET_KEY_AUTH, algorithm=ALGORITHM)
    return token


def build_confirmation_message(email: str, confirmation_url: str) -> MessageSchema:
    """
    Builds the message schema for a confirmation email.

    :param email: The recipient's email address.
    :param confirmation_url: The URL for the email confirmation.
    :return: A MessageSchema object ready to be sent.
    """
    body = EMAIL_BODY_TEMPLATE.format(confirmation_url=confirmation_url)
    return MessageSchema(
        subject=EMAIL_SUBJECT,
        recipients=[email],
        body=body,
        subtype=EMAIL_SUBTYPE
    )


async def send_confirmation_email(email: str, user_id: str) -> None:
    try:
        token = create_confirmation_token(user_id)
        confirmation_url = f"{CONFIRMATION_URL}{token}"
        message = build_confirmation_message(email, confirmation_url)
        fm = FastMail(get_connection_config())
        await fm.send_message(message)
        logger.info(f"send_confirmation_email - Email sent to {email}")
    except Exception as e:
        logger.error(f"send_confirmation_email - Failed to send email to {email}: {e}")
        raise send_confirmation_email_exception
