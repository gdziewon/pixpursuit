from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
from argon2 import PasswordHasher
import os
from dotenv import load_dotenv
from config.logging_config import setup_logging

load_dotenv()
logger = setup_logging(__name__)
ph = PasswordHasher()
SECRET_KEY = os.environ['AUTH_SECRET_KEY']
ALGORITHM = "HS256"


# TODO: Implement email confirmation
async def hash_password(password: str):
    return ph.hash(password)


def create_confirmation_token(user_id: str):
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def send_confirmation_email(email: str, user_id: str):
    token = create_confirmation_token(user_id)
    confirmation_url = f"http://pixpursuit/verify-email?token={token}"
    message = MessageSchema(
        subject="Email Confirmation",
        recipients=[email],
        body=f"Please confirm your email by clicking on this link: {confirmation_url}",
        subtype="html"
    )

    fm = FastMail(ConnectionConfig(...))
    await fm.send_message(message)
