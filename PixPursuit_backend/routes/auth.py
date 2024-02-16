from datetime import timedelta
from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from config.logging_config import setup_logging
from dotenv import load_dotenv
from authentication.auth import authenticate_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth_schema import Token
from utils.constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY_AUTH, ALGORITHM
from schemas.auth_schema import UserRegistration
from authentication.registration import hash_password, send_confirmation_email
from databases.database_tools import create_user, mark_email_as_verified
from jose import JWTError, jwt

load_dotenv()
logger = setup_logging(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning("/token - Incorrect username or password")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    logger.info(f"/token - Successfully provided token to user: {user['username']}")
    return {"access_token": access_token, "token_type": "bearer", "username": user['username']}


@router.post("/register")
async def register_user(data: UserRegistration, background_tasks: BackgroundTasks):
    password = data.password
    email = data.email

    hashed_password = await hash_password(password)
    new_user = await create_user(email, hashed_password)
    if not new_user:
        logger.error("/register - Failed to create user")
        raise HTTPException(status_code=500, detail="Failed to create user")

    background_tasks.add_task(send_confirmation_email, email, str(new_user.inserted_id))
    logger.info(f"/register - User registered successfully: {email}")
    return {"message": "User registered successfully. Please check your email to confirm registration."}


@router.get("/verify-email")
async def verify_email(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token")

        await mark_email_as_verified(user_id)
        return {"message": "Email verified successfully."}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
