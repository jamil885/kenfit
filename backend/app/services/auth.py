from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.user import create_user, get_user_by_email

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
):
    email = email.lower()
    existing_user = get_user_by_email(db, email.lower())

    if existing_user:
        raise ValueError("Email already registered")

    password_hash = hash_password(password)

    return create_user(
        db=db,
        name=name,
        email=email,
        password_hash=password_hash,
    )


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    user = get_user_by_email(db, email.lower())
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
