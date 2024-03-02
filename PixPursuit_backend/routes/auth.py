from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.auth_schema import Token, UserRegistration
from authentication.auth import authenticate_user, get_tokens
from authentication.registration import hash_password, send_confirmation_email
from databases.database_tools import create_user, mark_email_as_verified
from jose import JWTError, jwt
from utils.constants import SECRET_KEY_AUTH, ALGORITHM
from authentication.auth import get_current_user_refresh

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    if '@' in username:
        username = username.split('@')[0]

    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = get_tokens(user['username'])

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "username": user['username']}


@router.post("/register")
async def register_user(user_registration: UserRegistration, background_tasks: BackgroundTasks):
    new_user = await create_user(user_registration.email, await hash_password(user_registration.password))
    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    background_tasks.add_task(send_confirmation_email, user_registration.email, new_user.inserted_id)
    return {"message": "User registered successfully. Please check your email to confirm registration."}


@router.get("/verify-email")
async def verify_email(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        if not payload.get("user_id"):
            raise HTTPException(status_code=400, detail="Invalid token")

        await mark_email_as_verified(payload["user_id"])
        return {"message": "Email verified successfully."}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str = Depends(oauth2_scheme)):
    user = await get_current_user_refresh(refresh_token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = get_tokens(user.username)

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "username": user.username}
