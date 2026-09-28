from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.workout_exercise import WorkoutExercise
from app.repositories.exercise import get_exercise_by_id
from app.repositories.workout_exercise import (
    create_workout_exercise,
    delete_workout_exercise,
    get_workout_exercise_by_id,
    get_workout_exercises,
)
from app.schemas.workout_exercise import WorkoutExerciseCreate
from app.services.workout import get_user_workout


def add_exercise_to_workout(
    db: Session,
    user_id: int,
    workout_id: int,
    data: WorkoutExerciseCreate,
) -> WorkoutExercise:
    get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )

    exercise = get_exercise_by_id(
        db=db,
        exercise_id=data.exercise_id,
    )

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    return create_workout_exercise(
        db=db,
        workout_id=workout_id,
        **data.model_dump(),
    )


def get_exercises_for_workout(
    db: Session,
    user_id: int,
    workout_id: int,
) -> list[WorkoutExercise]:
    get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )

    return get_workout_exercises(
        db=db,
        workout_id=workout_id,
    )


def remove_exercise_from_workout(
    db: Session,
    user_id: int,
    workout_id: int,
    workout_exercise_id: int,
) -> None:
    get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )

    workout_exercise = get_workout_exercise_by_id(
        db=db,
        workout_exercise_id=workout_exercise_id,
    )

    if (
        workout_exercise is None
        or workout_exercise.workout_id != workout_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found",
        )

    delete_workout_exercise(
        db=db,
        workout_exercise=workout_exercise,
    )