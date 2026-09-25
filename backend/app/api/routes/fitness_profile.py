from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.fitness_profile import (
    FitnessProfileCreate,
    FitnessProfileResponse,
    FitnessProfileUpdate,
)
from app.services.fitness_profile import (
    get_user_fitness_profile,
    register_fitness_profile,
    update_user_fitness_profile,
)

router = APIRouter(
    prefix="/fitness-profile",
    tags=["Fitness Profile"],
)


@router.post(
    "",
    response_model=FitnessProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    profile: FitnessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return register_fitness_profile(
            db=db,
            user_id=current_user.id,
            birth_date=profile.birth_date,
            gender=profile.gender,
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            fitness_level=profile.fitness_level,
            goal=profile.goal,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=FitnessProfileResponse,
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_user_fitness_profile(
        db=db,
        user_id=current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fitness profile not found",
        )

    return profile


@router.put(
    "",
    response_model=FitnessProfileResponse,
)
def update_profile(
    profile: FitnessProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_user_fitness_profile(
            db=db,
            user_id=current_user.id,
            data=profile.model_dump(exclude_unset=True),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error