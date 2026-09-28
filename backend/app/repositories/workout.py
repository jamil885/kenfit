from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workout import Workout


def create_workout(
    db: Session,
    name: str,
    description: str | None,
    owner_id: int | None,
    source: str,
) -> Workout:
    workout = Workout(
        name=name,
        description=description,
        owner_id=owner_id,
        source=source,
    )

    db.add(workout)
    db.commit()
    db.refresh(workout)

    return workout


def get_workout_by_id(
    db: Session,
    workout_id: int,
) -> Workout | None:
    statement = select(Workout).where(
        Workout.id == workout_id
    )

    return db.scalar(statement)


def get_workouts_by_owner(
    db: Session,
    owner_id: int,
) -> list[Workout]:
    statement = (
        select(Workout)
        .where(Workout.owner_id == owner_id)
        .order_by(Workout.id)
    )

    return list(db.scalars(statement).all())


def update_workout(
    db: Session,
    workout: Workout,
    name: str | None = None,
    description: str | None = None,
) -> Workout:
    if name is not None:
        workout.name = name

    if description is not None:
        workout.description = description

    db.commit()
    db.refresh(workout)

    return workout


def delete_workout(
    db: Session,
    workout: Workout,
) -> None:
    db.delete(workout)
    db.commit()