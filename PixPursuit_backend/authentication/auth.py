from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from databases.database_tools import get_user
from argon2 import PasswordHasher
import argon2.exceptions
from config.logging_config import setup_logging
from schemas.auth_schema import TokenData, User
from utils.constants import SECRET_KEY_AUTH, ALGORITHM

logger = setup_logging(__name__)
ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_password(plain_password, hashed_password):
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False

    if not user['verified']:
        return False

    try:
        valid_password = await verify_password(password, user['password'])
    except argon2.exceptions.InvalidHashError:
        logger.error(f"Invalid hash for user {username}")
        valid_password = False
    return user if valid_password else False


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_AUTH, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
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
