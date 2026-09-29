from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.exercise_muscle import ExerciseMuscle
from app.models.muscle_group import MuscleGroup
from app.repositories.exercise import (
    delete_exercise,
    get_exercise_by_id,
    get_exercises,
    update_exercise,
)
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate


def create_user_exercise(
    db: Session,
    user_id: int,
    data: ExerciseCreate,
) -> Exercise:
    exercise = Exercise(
        name=data.name,
        description=data.description,
        discipline=data.discipline,
        modality=data.modality,
        exercise_type=data.exercise_type,
        equipment=data.equipment,
        difficulty=data.difficulty,
        instructions=data.instructions,
        owner_id=user_id,
        source="USER",
    )

    db.add(exercise)
    db.flush()

    for muscle in data.muscle_groups:
        muscle_group = db.execute(
            select(MuscleGroup).where(
                MuscleGroup.id == muscle.muscle_group_id
            )
        ).scalar_one_or_none()

        if muscle_group is None:
            db.rollback()
            raise ValueError(
                f"Muscle group {muscle.muscle_group_id} does not exist"
            )

        exercise_muscle = ExerciseMuscle(
            exercise_id=exercise.id,
            muscle_group_id=muscle.muscle_group_id,
            role=muscle.role,
        )

        db.add(exercise_muscle)

    db.commit()
    db.refresh(exercise)

    return exercise


def get_exercise(
    db: Session,
    user_id: int,
    exercise_id: int,
) -> Exercise | None:
    exercise = get_exercise_by_id(
        db=db,
        exercise_id=exercise_id,
    )

    if exercise is None:
        return None

    if (
        exercise.source != "SYSTEM"
        and exercise.owner_id != user_id
    ):
        return None

    return exercise


def list_exercises(
    db: Session,
    user_id: int,
) -> list[Exercise]:
    return get_exercises(
        db=db,
        owner_id=user_id,
    )

def update_user_exercise(
    db: Session,
    user_id: int,
    exercise_id: int,
    data: ExerciseUpdate,
) -> Exercise | None:
    exercise = get_exercise_by_id(
        db,
        exercise_id,
    )

    if exercise is None:
        return None

    if exercise.source != "USER" or exercise.owner_id != user_id:
        raise PermissionError(
            "You do not have permission to modify this exercise"
        )

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"muscle_groups"},
    )

    for field, value in update_data.items():
        setattr(exercise, field, value)

    if data.muscle_groups is not None:
        exercise.muscle_groups.clear()

        for muscle in data.muscle_groups:
            muscle_group = db.execute(
                select(MuscleGroup).where(
                    MuscleGroup.id == muscle.muscle_group_id
                )
            ).scalar_one_or_none()

            if muscle_group is None:
                db.rollback()
                raise ValueError(
                    f"Muscle group {muscle.muscle_group_id} does not exist"
                )

            exercise.muscle_groups.append(
                ExerciseMuscle(
                    muscle_group_id=muscle.muscle_group_id,
                    role=muscle.role,
                )
            )

    return update_exercise(
        db,
        exercise,
    )


def delete_user_exercise(
    db: Session,
    user_id: int,
    exercise_id: int,
) -> bool:
    exercise = get_exercise_by_id(
        db,
        exercise_id,
    )

    if exercise is None:
        return False

    if exercise.source != "USER" or exercise.owner_id != user_id:
        raise PermissionError(
            "You do not have permission to delete this exercise"
        )

    delete_exercise(
        db,
        exercise,
    )

    return True