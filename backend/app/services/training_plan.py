from sqlalchemy.orm import Session

from app.models.training_plan import TrainingPlan
from app.repositories.training_plan import (
    create_training_plan,
    delete_training_plan,
    get_training_plan_by_id,
    get_training_plans_for_user,
    update_training_plan,
)
from app.schemas.training_plan import (
    TrainingPlanCreate,
    TrainingPlanUpdate,
)
from app.services.split import get_visible_split


def validate_split(
    db: Session,
    user_id: int,
    split_id: int,
) -> None:
    split = get_visible_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        raise ValueError("Split not found")


def create_user_training_plan(
    db: Session,
    user_id: int,
    data: TrainingPlanCreate,
) -> TrainingPlan:
    validate_split(
        db=db,
        user_id=user_id,
        split_id=data.split_id,
    )

    return create_training_plan(
        db=db,
        name=data.name,
        description=data.description,
        goal=data.goal,
        duration_weeks=data.duration_weeks,
        split_id=data.split_id,
        owner_id=user_id,
        source="USER",
    )


def get_user_training_plans(
    db: Session,
    user_id: int,
) -> list[TrainingPlan]:
    return get_training_plans_for_user(
        db=db,
        user_id=user_id,
    )


def get_visible_training_plan(
    db: Session,
    user_id: int,
    training_plan_id: int,
) -> TrainingPlan | None:
    training_plan = get_training_plan_by_id(
        db=db,
        training_plan_id=training_plan_id,
    )

    if training_plan is None:
        return None

    if (
        training_plan.source != "SYSTEM"
        and training_plan.owner_id != user_id
    ):
        return None

    return training_plan


def get_owned_training_plan(
    db: Session,
    user_id: int,
    training_plan_id: int,
) -> TrainingPlan | None:
    training_plan = get_training_plan_by_id(
        db=db,
        training_plan_id=training_plan_id,
    )

    if training_plan is None:
        return None

    if (
        training_plan.source != "USER"
        or training_plan.owner_id != user_id
    ):
        raise PermissionError(
            "You do not have permission to modify this training plan"
        )

    return training_plan


def update_user_training_plan(
    db: Session,
    user_id: int,
    training_plan_id: int,
    data: TrainingPlanUpdate,
) -> TrainingPlan | None:
    training_plan = get_owned_training_plan(
        db=db,
        user_id=user_id,
        training_plan_id=training_plan_id,
    )

    if training_plan is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "split_id" in update_data:
        validate_split(
            db=db,
            user_id=user_id,
            split_id=update_data["split_id"],
        )

    for field, value in update_data.items():
        setattr(training_plan, field, value)

    return update_training_plan(
        db=db,
        training_plan=training_plan,
    )


def delete_user_training_plan(
    db: Session,
    user_id: int,
    training_plan_id: int,
) -> bool:
    training_plan = get_owned_training_plan(
        db=db,
        user_id=user_id,
        training_plan_id=training_plan_id,
    )

    if training_plan is None:
        return False

    delete_training_plan(
        db=db,
        training_plan=training_plan,
    )

    return True