from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.workout_exercise import WorkoutExercise
from app.repositories.exercise import get_exercise_by_id
from app.repositories.workout_exercise import (
    create_workout_exercise,
    delete_workout_exercise,
    get_workout_exercise_by_id,
    get_workout_exercises,
    save_workout_exercise_order,
    update_workout_exercise,
)
from app.schemas.workout_exercise import (
    WorkoutExerciseCreate,
    WorkoutExerciseReorder,
    WorkoutExerciseUpdate,
)
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

def update_exercise_in_workout(
    db: Session,
    user_id: int,
    workout_id: int,
    workout_exercise_id: int,
    data: WorkoutExerciseUpdate,
) -> WorkoutExercise:
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

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(workout_exercise, field, value)

    return update_workout_exercise(
        db=db,
        workout_exercise=workout_exercise,
    )

def reorder_workout_exercises(
    db: Session,
    user_id: int,
    workout_id: int,
    data: WorkoutExerciseReorder,
) -> list[WorkoutExercise]:
    get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )

    workout_exercises = get_workout_exercises(
        db=db,
        workout_id=workout_id,
    )

    existing_by_id = {
        item.id: item
        for item in workout_exercises
    }

    received_ids = [
        item.workout_exercise_id
        for item in data.exercises
    ]

    if len(received_ids) != len(set(received_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate workout exercise IDs",
        )

    if set(received_ids) != set(existing_by_id.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All workout exercises must be included",
        )

    received_orders = [
        item.order
        for item in data.exercises
    ]

    expected_orders = list(
        range(1, len(workout_exercises) + 1)
    )

    if sorted(received_orders) != expected_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Orders must be consecutive starting from 1",
        )

    for item in data.exercises:
        existing_by_id[item.workout_exercise_id].order = item.order

    updated = save_workout_exercise_order(
        db=db,
        workout_exercises=workout_exercises,
    )

    return sorted(
        updated,
        key=lambda item: item.order,
    )