from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.workout import (
    create_workout,
    delete_workout,
    get_workout_by_id,
    get_workouts_by_owner,
    update_workout,
)
from app.schemas.workout import WorkoutCreate, WorkoutUpdate


def create_user_workout(
    db: Session,
    user_id: int,
    data: WorkoutCreate,
) -> Workout:
    return create_workout(
        db=db,
        name=data.name,
        description=data.description,
        owner_id=user_id,
        source="USER",
    )


def get_user_workouts(
    db: Session,
    user_id: int,
) -> list[Workout]:
    return get_workouts_by_owner(
        db=db,
        owner_id=user_id,
    )


def get_user_workout(
    db: Session,
    user_id: int,
    workout_id: int,
) -> Workout:
    workout = get_workout_by_id(
        db=db,
        workout_id=workout_id,
    )

    if workout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )

    if workout.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this workout",
        )

    return workout


def update_user_workout(
    db: Session,
    user_id: int,
    workout_id: int,
    data: WorkoutUpdate,
) -> Workout:
    workout = get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        workout.name = update_data["name"]

    if "description" in update_data:
        workout.description = update_data["description"]

    db.commit()
    db.refresh(workout)

    return workout


def delete_user_workout(
    db: Session,
    user_id: int,
    workout_id: int,
) -> None:
    workout = get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )

    delete_workout(
        db=db,
        workout=workout,
    )