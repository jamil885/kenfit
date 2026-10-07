from pydantic import EmailStr, Field

from app.schemas.common import Schema


class UserCreate(Schema):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(Schema):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    model_config = {"from_attributes": True}


class UserLogin(Schema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(Schema):
    access_token: str
    token_type: str
