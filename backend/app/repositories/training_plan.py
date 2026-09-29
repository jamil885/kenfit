from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.training_plan import TrainingPlan


def create_training_plan(
    db: Session,
    name: str,
    description: str | None,
    goal: str | None,
    duration_weeks: int | None,
    split_id: int,
    owner_id: int | None,
    source: str,
) -> TrainingPlan:
    training_plan = TrainingPlan(
        name=name,
        description=description,
        goal=goal,
        duration_weeks=duration_weeks,
        split_id=split_id,
        owner_id=owner_id,
        source=source,
    )

    db.add(training_plan)
    db.commit()
    db.refresh(training_plan)

    return training_plan


def get_training_plan_by_id(
    db: Session,
    training_plan_id: int,
) -> TrainingPlan | None:
    statement = select(TrainingPlan).where(
        TrainingPlan.id == training_plan_id
    )

    return db.scalar(statement)


def get_training_plans_for_user(
    db: Session,
    user_id: int,
) -> list[TrainingPlan]:
    statement = (
        select(TrainingPlan)
        .where(
            or_(
                TrainingPlan.source == "SYSTEM",
                TrainingPlan.owner_id == user_id,
            )
        )
        .order_by(TrainingPlan.id)
    )

    return list(
        db.scalars(statement).all()
    )


def update_training_plan(
    db: Session,
    training_plan: TrainingPlan,
) -> TrainingPlan:
    db.commit()
    db.refresh(training_plan)

    return training_plan


def delete_training_plan(
    db: Session,
    training_plan: TrainingPlan,
) -> None:
    db.delete(training_plan)
    db.commit()