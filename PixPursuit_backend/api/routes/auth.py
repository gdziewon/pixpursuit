"""
api/routes/auth.py

Defines the authentication routes for the application, handling user login, registration,
token refresh, and email verification.
"""

from fastapi import Depends, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from api.schemas.auth_schema import Token, UserRegistration
from services.authentication.auth import authenticate_user, get_tokens
from services.authentication.registration import hash_password, send_confirmation_email
from data.databases.mongodb.async_db.database_tools import create_user, mark_email_as_verified
from jose import jwt
from utils.constants import SECRET_KEY_AUTH, ALGORITHM
from services.authentication.auth import get_current_user_refresh
from utils.exceptions import invalid_token_exception, create_user_exception, verify_email_exception

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
        Authenticate a user and return access and refresh tokens.

        :param form_data: The OAuth2 password request form data.
        :type form_data: OAuth2PasswordRequestForm
        :return: An object containing the access token, refresh token, token type, and username.
        :rtype: Token
    """
    username = form_data.username
    password = form_data.password
    if '@' in username:
        username = username.split('@')[0]

    user = await authenticate_user(username, password)
    if not user:
        raise invalid_token_exception

    access_token, refresh_token = get_tokens(user['username'])

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "username": user['username']}


@router.post("/register")
async def register_user(user_registration: UserRegistration, background_tasks: BackgroundTasks):
    """
    Register a new user and send a confirmation email.

    :param user_registration: The data needed for registering a new user.
    :type user_registration: UserRegistration
    :param background_tasks: Background tasks for sending confirmation email.
    :type background_tasks: BackgroundTasks
    :return: A message indicating successful registration.
    :rtype: dict
    """
    new_user = await create_user(user_registration.email, await hash_password(user_registration.password))
    if not new_user:
        raise create_user_exception

    background_tasks.add_task(send_confirmation_email, user_registration.email, str(new_user.inserted_id))
    return {"message": "User registered successfully. Please check your email to confirm registration."}


@router.get("/verify-email")
async def verify_email(token: str):
    """
        Verify a user's email address.

        :param token: The token used to verify the email address.
        :type token: str
        :return: A message indicating successful email verification.
        :rtype: dict
    """
    payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
    if not payload.get("user_id"):
        raise invalid_token_exception

    success = await mark_email_as_verified(payload["user_id"])
    if not success:
        raise verify_email_exception

    return {"message": "Email verified successfully."}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str = Depends(oauth2_scheme)):
    """
        Refresh the access token using the refresh token.

        :param refresh_token: The refresh token used to obtain new access tokens.
        :type refresh_token: str
        :return: An object containing the new access token, refresh token, token type, and username.
        :rtype: Token
    """
    user = await get_current_user_refresh(refresh_token)
    if not user:
        raise invalid_token_exception

    access_token, refresh_token = get_tokens(user.username)

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "username": user.username}
