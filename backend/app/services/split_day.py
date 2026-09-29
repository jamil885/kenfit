from sqlalchemy.orm import Session

from app.models.split_day import SplitDay
from app.repositories.split_day import (
    create_split_day,
    delete_split_day,
    get_split_day_by_id,
    get_split_days,
    update_split_day,
)
from app.schemas.split_day import (
    SplitDayCreate,
    SplitDayUpdate,
)
from app.services.split import get_owned_split
from app.services.workout import get_user_workout


def validate_workout(
    db: Session,
    user_id: int,
    workout_id: int | None,
) -> None:
    if workout_id is None:
        return

    get_user_workout(
        db=db,
        user_id=user_id,
        workout_id=workout_id,
    )


def add_day_to_split(
    db: Session,
    user_id: int,
    split_id: int,
    data: SplitDayCreate,
) -> SplitDay:
    split = get_owned_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        raise ValueError("Split not found")

    validate_workout(
        db=db,
        user_id=user_id,
        workout_id=data.workout_id,
    )

    return create_split_day(
        db=db,
        split_id=split_id,
        workout_id=data.workout_id,
        order=data.order,
        name=data.name,
    )


def get_days_for_split(
    db: Session,
    user_id: int,
    split_id: int,
) -> list[SplitDay]:
    split = get_owned_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        raise ValueError("Split not found")

    return get_split_days(
        db=db,
        split_id=split_id,
    )


def update_day_in_split(
    db: Session,
    user_id: int,
    split_id: int,
    split_day_id: int,
    data: SplitDayUpdate,
) -> SplitDay | None:
    split = get_owned_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        return None

    split_day = get_split_day_by_id(
        db=db,
        split_day_id=split_day_id,
    )

    if (
        split_day is None
        or split_day.split_id != split_id
    ):
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "workout_id" in update_data:
        validate_workout(
            db=db,
            user_id=user_id,
            workout_id=update_data["workout_id"],
        )

    for field, value in update_data.items():
        setattr(split_day, field, value)

    return update_split_day(
        db=db,
        split_day=split_day,
    )


def remove_day_from_split(
    db: Session,
    user_id: int,
    split_id: int,
    split_day_id: int,
) -> bool:
    split = get_owned_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        return False

    split_day = get_split_day_by_id(
        db=db,
        split_day_id=split_day_id,
    )

    if (
        split_day is None
        or split_day.split_id != split_id
    ):
        return False

    delete_split_day(
        db=db,
        split_day=split_day,
    )

    return True