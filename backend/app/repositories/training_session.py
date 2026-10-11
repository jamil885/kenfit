from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.training_session import TrainingSession


def create_training_session(
    db: Session,
    user_id: int,
    workout_id: int | None,
    training_plan_id: int | None,
    started_at: datetime,
    notes: str | None,
) -> TrainingSession:
    training_session = TrainingSession(
        user_id=user_id,
        workout_id=workout_id,
        training_plan_id=training_plan_id,
        started_at=started_at,
        finished_at=None,
        status="IN_PROGRESS",
        notes=notes,
    )

    db.add(training_session)
    db.commit()
    db.refresh(training_session)

    return training_session


def get_training_session_by_id(
    db: Session,
    training_session_id: int,
) -> TrainingSession | None:
    statement = select(TrainingSession).where(TrainingSession.id == training_session_id)

    return db.scalar(statement)


def get_training_sessions_by_user(
    db: Session,
    user_id: int,
) -> list[TrainingSession]:
    statement = (
        select(TrainingSession)
        .where(TrainingSession.user_id == user_id)
        .order_by(TrainingSession.started_at.desc())
    )

    return list(db.scalars(statement).all())


def update_training_session(
    db: Session,
    training_session: TrainingSession,
) -> TrainingSession:
    db.commit()
    db.refresh(training_session)

    return training_session
