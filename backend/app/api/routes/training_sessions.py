from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionResponse,
    TrainingSessionUpdate,
)
from app.services.training_session import (
    cancel_training_session,
    complete_training_session,
    get_user_training_session,
    get_user_training_sessions,
    start_training_session,
    update_user_training_session,
)

router = APIRouter(
    prefix="/training-sessions",
    tags=["Training Sessions"],
)


@router.post(
    "",
    response_model=TrainingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_session(
    data: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return start_training_session(
            db=db,
            user_id=current_user.id,
            data=data,
        )

    except (ValueError, PermissionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[TrainingSessionResponse],
)
def get_training_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_training_sessions(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{training_session_id}",
    response_model=TrainingSessionResponse,
)
def get_training_session(
    training_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training_session = get_user_training_session(
        db=db,
        user_id=current_user.id,
        training_session_id=training_session_id,
    )

    if training_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        )

    return training_session


@router.patch(
    "/{training_session_id}",
    response_model=TrainingSessionResponse,
)
def update_training_session(
    training_session_id: int,
    data: TrainingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training_session = update_user_training_session(
        db=db,
        user_id=current_user.id,
        training_session_id=training_session_id,
        data=data,
    )

    if training_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        )

    return training_session


@router.post(
    "/{training_session_id}/complete",
    response_model=TrainingSessionResponse,
)
def complete_session(
    training_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        training_session = complete_training_session(
            db=db,
            user_id=current_user.id,
            training_session_id=training_session_id,
        )

        if training_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found",
            )

        return training_session

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/{training_session_id}/cancel",
    response_model=TrainingSessionResponse,
)
def cancel_session(
    training_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        training_session = cancel_training_session(
            db=db,
            user_id=current_user.id,
            training_session_id=training_session_id,
        )

        if training_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found",
            )

        return training_session

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
