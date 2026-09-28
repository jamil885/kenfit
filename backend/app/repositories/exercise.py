from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise


def create_exercise(
    db: Session,
    exercise: Exercise,
) -> Exercise:
    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    return exercise


def get_exercise_by_id(
    db: Session,
    exercise_id: int,
) -> Exercise | None:
    result = db.execute(
        select(Exercise).where(
            Exercise.id == exercise_id
        )
    )

    return result.scalar_one_or_none()


def get_exercises(
    db: Session,
) -> list[Exercise]:
    result = db.execute(
        select(Exercise)
        .where(Exercise.is_active.is_(True))
        .order_by(Exercise.id)
    )

    return list(result.scalars().all())


def update_exercise(
    db: Session,
    exercise: Exercise,
) -> Exercise:
    db.commit()
    db.refresh(exercise)

    return exercise


def delete_exercise(
    db: Session,
    exercise: Exercise,
) -> None:
    db.delete(exercise)
    db.commit()