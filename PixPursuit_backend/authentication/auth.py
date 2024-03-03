from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from databases.database_tools import get_user
from argon2 import PasswordHasher
import argon2.exceptions
from config.logging_config import setup_logging
from schemas.auth_schema import TokenData, User
from utils.constants import SECRET_KEY_AUTH, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from utils.exceptions import credentials_exception, invalid_credentials_exception, create_token_exception

logger = setup_logging(__name__)

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False


async def authenticate_user(username: str, password: str) -> dict:
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


def create_token(data: dict, expires_delta: timedelta = None) -> str or None:
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
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_token(
            data={"sub": username,
                  "type": "access"},
            expires_delta=access_token_expires
        )

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


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> User or None:
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        typ: str = payload.get("type")
        if username is None or typ != "access":
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    user_model = User(**user)
    request.state.username = user_model.username
    return user_model


async def get_current_user_refresh(token: str = Depends(oauth2_scheme)) -> User or None:
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        typ: str = payload.get("type")
        if username is None or typ != "refresh":
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    user_model = User(**user)
    return user_model
