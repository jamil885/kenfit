from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.training import TrainingPlan, Workout
from app.models.training_session import TrainingSession
from app.repositories.training_session import (
    create_training_session,
    get_training_session_by_id,
    get_training_sessions_by_user,
    update_training_session,
)
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
)
from app.services.content import readable


def validate_workout(
    db: Session,
    user_id: int,
    workout_id: int | None,
) -> None:
    if workout_id is None:
        return

    workout = readable(db, Workout, workout_id, user_id)

    if workout is None:
        raise ValueError("Workout not found")


def validate_training_plan(
    db: Session,
    user_id: int,
    training_plan_id: int | None,
) -> None:
    if training_plan_id is None:
        return

    training_plan = readable(db, TrainingPlan, training_plan_id, user_id)

    if training_plan is None:
        raise ValueError("Training plan not found")


def start_training_session(
    db: Session,
    user_id: int,
    data: TrainingSessionCreate,
) -> TrainingSession:
    validate_workout(
        db=db,
        user_id=user_id,
        workout_id=data.workout_id,
    )

    validate_training_plan(
        db=db,
        user_id=user_id,
        training_plan_id=data.training_plan_id,
    )

    return create_training_session(
        db=db,
        user_id=user_id,
        workout_id=data.workout_id,
        training_plan_id=data.training_plan_id,
        started_at=datetime.now(timezone.utc),
        notes=data.notes,
    )


def get_user_training_sessions(
    db: Session,
    user_id: int,
) -> list[TrainingSession]:
    return get_training_sessions_by_user(
        db=db,
        user_id=user_id,
    )


def get_user_training_session(
    db: Session,
    user_id: int,
    training_session_id: int,
) -> TrainingSession | None:
    training_session = get_training_session_by_id(
        db=db,
        training_session_id=training_session_id,
    )

    if training_session is None:
        return None

    if training_session.user_id != user_id:
        return None

    return training_session


def update_user_training_session(
    db: Session,
    user_id: int,
    training_session_id: int,
    data: TrainingSessionUpdate,
) -> TrainingSession | None:
    training_session = get_user_training_session(
        db=db,
        user_id=user_id,
        training_session_id=training_session_id,
    )

    if training_session is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(training_session, field, value)

    return update_training_session(
        db=db,
        training_session=training_session,
    )


def complete_training_session(
    db: Session,
    user_id: int,
    training_session_id: int,
) -> TrainingSession | None:
    training_session = get_user_training_session(
        db=db,
        user_id=user_id,
        training_session_id=training_session_id,
    )

    if training_session is None:
        return None

    if training_session.status != "IN_PROGRESS":
        raise ValueError("Only an in-progress training session can be completed")

    training_session.status = "COMPLETED"
    training_session.finished_at = datetime.now(timezone.utc)

    return update_training_session(
        db=db,
        training_session=training_session,
    )


def cancel_training_session(
    db: Session,
    user_id: int,
    training_session_id: int,
) -> TrainingSession | None:
    training_session = get_user_training_session(
        db=db,
        user_id=user_id,
        training_session_id=training_session_id,
    )

    if training_session is None:
        return None

    if training_session.status != "IN_PROGRESS":
        raise ValueError("Only an in-progress training session can be cancelled")

    training_session.status = "CANCELLED"
    training_session.finished_at = datetime.now(timezone.utc)

    return update_training_session(
        db=db,
        training_session=training_session,
    )
