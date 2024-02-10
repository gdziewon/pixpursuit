from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
from argon2 import PasswordHasher
from dotenv import load_dotenv
from config.logging_config import setup_logging
from utils.constants import SECRET_KEY_AUTH, ALGORITHM, MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_FROM_NAME

load_dotenv()
logger = setup_logging(__name__)
ph = PasswordHasher()

conf = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_FROM_NAME=MAIL_FROM_NAME,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )


async def hash_password(password: str):
    return ph.hash(password)


def create_confirmation_token(user_id: str):
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_KEY_AUTH, algorithm=ALGORITHM)
    return token


async def send_confirmation_email(email, user_id):
    token = create_confirmation_token(str(user_id))
    confirmation_url = f"http://pixpursuit/verify-email?token={token}"
    message = MessageSchema(
        subject="PixPursuit - Email Confirmation",
        recipients=[email],
        body=f"Please confirm your email by clicking on this link: {confirmation_url}\n\n "
             f"If you did not register to PixPursuit, please ignore this email.",
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
