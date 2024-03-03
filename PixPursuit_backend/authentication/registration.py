from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
from argon2 import PasswordHasher
from config.logging_config import setup_logging
from utils.constants import SECRET_KEY_AUTH, ALGORITHM, MAIL_USERNAME, MAIL_APP_PASSWORD, \
                            MAIL_FROM, MAIL_FROM_NAME, CONFIRMATION_URL

logger = setup_logging(__name__)

ph = PasswordHasher()
connection_config = ConnectionConfig(
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
    return ph.hash(password)


def create_confirmation_token(user_id: str) -> str:
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_KEY_AUTH, algorithm=ALGORITHM)
    return token


async def send_confirmation_email(email: str, user_id: str) -> None:
    try:
        token = create_confirmation_token(user_id)
        confirmation_url = f"{CONFIRMATION_URL}{token}"
        message = MessageSchema(
            subject="PixPursuit - Email Confirmation",
            recipients=[email],
            body=f"Please confirm your email by clicking on this link:\n\n{confirmation_url}\n\n "
                 f"If you did not register to PixPursuit, please ignore this email.",
            subtype="html"
        )
        fm = FastMail(connection_config)
        await fm.send_message(message)
        logger.info(f"send_confirmation_email - Email sent to {email}")
    except Exception as e:
        logger.error(f"send_confirmation_email - Failed to send email to {email}: {e}")
