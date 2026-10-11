from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.account import DeleteAccountRequest, PasswordResetRequest, RecoveryRequest
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import account
from app.services.auth import (
    authenticate_user,
    create_access_token,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return register_user(
            db=db,
            name=user.name,
            email=user.email,
            password=user.password,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    authenticated_user = authenticate_user(
        db=db,
        email=user.email,
        password=user.password,
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(authenticated_user.id, authenticated_user.token_version)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/forgot-password")
def forgot_password(
    data: RecoveryRequest, request: Request, tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    if not account.rate_limit(
        db, "recovery-ip", request.client.host if request.client else "unknown", 20
    ):
        raise HTTPException(429, "Too many attempts. Try again later.")
    return account.request_reset(db, str(data.email), tasks)


@router.post("/reset-password")
def reset_password(
    data: PasswordResetRequest,
    request: Request,
    tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not account.rate_limit(
        db, "reset-ip", request.client.host if request.client else "unknown", 20
    ):
        raise HTTPException(429, "Too many attempts. Try again later.")
    return account.reset_password(db, data.token, data.password, tasks)


@router.delete("/me", status_code=204)
def delete_me(
    data: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not account.rate_limit(db, "delete-account", str(current_user.id), 5):
        raise HTTPException(429, "Too many attempts. Try again later.")
    try:
        account.delete_account(db, current_user, data.password)
    except (IntegrityError, ValueError) as error:
        db.rollback()
        raise HTTPException(409, "Account deletion could not be completed") from error
    return Response(status_code=204)
