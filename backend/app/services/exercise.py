from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.exercise_muscle import ExerciseMuscle
from app.models.muscle_group import MuscleGroup
from app.repositories.exercise import (
    create_exercise,
    get_exercise_by_id,
    get_exercises,
    update_exercise,
    delete_exercise,
)
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate


def create_user_exercise(
    db: Session,
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
    exercise_id: int,
) -> Exercise | None:
    return get_exercise_by_id(
        db,
        exercise_id,
    )


def list_exercises(
    db: Session,
) -> list[Exercise]:
    return get_exercises(db)


def update_user_exercise(
    db: Session,
    exercise_id: int,
    data: ExerciseUpdate,
) -> Exercise | None:
    exercise = get_exercise_by_id(
        db,
        exercise_id,
    )

    if exercise is None:
        return None

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
    exercise_id: int,
) -> bool:
    exercise = get_exercise_by_id(
        db,
        exercise_id,
    )

    if exercise is None:
        return False

    delete_exercise(
        db,
        exercise,
    )

    return True