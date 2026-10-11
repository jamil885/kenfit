from pydantic import EmailStr, Field

from app.schemas.common import Schema


class RecoveryRequest(Schema):
    email: EmailStr


class PasswordResetRequest(Schema):
    token: str = Field(min_length=32, max_length=128)
    password: str = Field(min_length=8, max_length=128)


class DeleteAccountRequest(Schema):
    password: str = Field(min_length=8, max_length=128)
