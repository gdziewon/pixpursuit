from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    disabled: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserRegistration(BaseModel):
    email: str
    password: str
