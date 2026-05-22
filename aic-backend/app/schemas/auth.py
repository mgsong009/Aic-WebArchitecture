from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    user_id: str
    password: str
    role: str


class UserInfo(BaseModel):
    id: int
    name: str
    role: str
    class_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class RefreshResponse(BaseModel):
    access_token: str
