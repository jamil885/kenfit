from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workout_exercise import WorkoutExercise


def create_workout_exercise(
    db: Session,
    workout_id: int,
    exercise_id: int,
    order: int,
    sets: int | None = None,
    reps: int | None = None,
    duration_seconds: int | None = None,
    distance_meters: float | None = None,
    load_kg: float | None = None,
    intensity: str | None = None,
    rest_seconds: int | None = None,
    tempo: str | None = None,
    notes: str | None = None,
) -> WorkoutExercise:
    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        order=order,
        sets=sets,
        reps=reps,
        duration_seconds=duration_seconds,
        distance_meters=distance_meters,
        load_kg=load_kg,
        intensity=intensity,
        rest_seconds=rest_seconds,
        tempo=tempo,
        notes=notes,
    )

    db.add(workout_exercise)
    db.commit()
    db.refresh(workout_exercise)

    return workout_exercise


def get_workout_exercise_by_id(
    db: Session,
    workout_exercise_id: int,
) -> WorkoutExercise | None:
    statement = select(WorkoutExercise).where(
        WorkoutExercise.id == workout_exercise_id
    )

    return db.scalar(statement)


def get_workout_exercises(
    db: Session,
    workout_id: int,
) -> list[WorkoutExercise]:
    statement = (
        select(WorkoutExercise)
        .where(WorkoutExercise.workout_id == workout_id)
        .order_by(WorkoutExercise.order)
    )

    return list(db.scalars(statement).all())


def delete_workout_exercise(
    db: Session,
    workout_exercise: WorkoutExercise,
) -> None:
    db.delete(workout_exercise)
    db.commit()

def update_workout_exercise(
    db: Session,
    workout_exercise: WorkoutExercise,
) -> WorkoutExercise:
    db.commit()
    db.refresh(workout_exercise)

    return workout_exercise

def save_workout_exercise_order(
    db: Session,
    workout_exercises: list[WorkoutExercise],
) -> list[WorkoutExercise]:
    db.commit()

    for workout_exercise in workout_exercises:
        db.refresh(workout_exercise)

    return workout_exercises