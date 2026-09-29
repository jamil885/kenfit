from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.training_plan import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
)
from app.services.training_plan import (
    create_user_training_plan,
    delete_user_training_plan,
    get_user_training_plans,
    get_visible_training_plan,
    update_user_training_plan,
)


router = APIRouter(
    prefix="/training-plans",
    tags=["Training Plans"],
)


@router.post(
    "",
    response_model=TrainingPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_plan(
    data: TrainingPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_user_training_plan(
            db=db,
            user_id=current_user.id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[TrainingPlanResponse],
)
def get_training_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_training_plans(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{training_plan_id}",
    response_model=TrainingPlanResponse,
)
def get_training_plan(
    training_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training_plan = get_visible_training_plan(
        db=db,
        user_id=current_user.id,
        training_plan_id=training_plan_id,
    )

    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found",
        )

    return training_plan


@router.patch(
    "/{training_plan_id}",
    response_model=TrainingPlanResponse,
)
def update_training_plan(
    training_plan_id: int,
    data: TrainingPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        training_plan = update_user_training_plan(
            db=db,
            user_id=current_user.id,
            training_plan_id=training_plan_id,
            data=data,
        )

        if training_plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training plan not found",
            )

        return training_plan

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{training_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_training_plan(
    training_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_user_training_plan(
            db=db,
            user_id=current_user.id,
            training_plan_id=training_plan_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training plan not found",
            )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc