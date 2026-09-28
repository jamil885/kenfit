from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User

from app.schemas.workout import (
    WorkoutCreate,
    WorkoutResponse,
    WorkoutUpdate,
)
from app.schemas.workout_exercise import (
    WorkoutExerciseCreate,
    WorkoutExerciseResponse,
)

from app.services.workout import (
    create_user_workout,
    delete_user_workout,
    get_user_workout,
    get_user_workouts,
    update_user_workout,
)
from app.services.workout_exercise import (
    add_exercise_to_workout,
    get_exercises_for_workout,
    remove_exercise_from_workout,
)


router = APIRouter(
    prefix="/workouts",
    tags=["Workouts"],
)


@router.post(
    "",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workout(
    data: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_user_workout(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "",
    response_model=list[WorkoutResponse],
)
def list_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_workouts(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{workout_id}",
    response_model=WorkoutResponse,
)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_workout(
        db=db,
        user_id=current_user.id,
        workout_id=workout_id,
    )


@router.patch(
    "/{workout_id}",
    response_model=WorkoutResponse,
)
def update_workout(
    workout_id: int,
    data: WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_workout(
        db=db,
        user_id=current_user.id,
        workout_id=workout_id,
        data=data,
    )


@router.delete(
    "/{workout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_user_workout(
        db=db,
        user_id=current_user.id,
        workout_id=workout_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{workout_id}/exercises",
    response_model=WorkoutExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_workout_exercise(
    workout_id: int,
    data: WorkoutExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_exercise_to_workout(
        db=db,
        user_id=current_user.id,
        workout_id=workout_id,
        data=data,
    )


@router.get(
    "/{workout_id}/exercises",
    response_model=list[WorkoutExerciseResponse],
)
def list_workout_exercises(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_exercises_for_workout(
        db=db,
        user_id=current_user.id,
        workout_id=workout_id,
    )


@router.delete(
    "/{workout_id}/exercises/{workout_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workout_exercise(
    workout_id: int,
    workout_exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    remove_exercise_from_workout(
        db=db,
        user_id=current_user.id,
        workout_id=workout_id,
        workout_exercise_id=workout_exercise_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)