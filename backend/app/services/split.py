from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.split import Split
from app.repositories.split import (
    create_split,
    delete_split,
    get_split_by_id,
    get_splits_for_user,
    update_split,
)
from app.schemas.split import SplitCreate, SplitUpdate


def create_user_split(
    db: Session,
    user_id: int,
    data: SplitCreate,
) -> Split:
    return create_split(
        db=db,
        name=data.name,
        description=data.description,
        owner_id=user_id,
        source="USER",
    )


def get_user_splits(
    db: Session,
    user_id: int,
) -> list[Split]:
    return get_splits_for_user(
        db=db,
        user_id=user_id,
    )


def get_visible_split(
    db: Session,
    user_id: int,
    split_id: int,
) -> Split | None:
    split = get_split_by_id(
        db=db,
        split_id=split_id,
    )

    if split is None:
        return None

    if (
        split.source != "SYSTEM"
        and split.owner_id != user_id
    ):
        return None

    return split


def get_owned_split(
    db: Session,
    user_id: int,
    split_id: int,
) -> Split | None:
    split = get_split_by_id(
        db=db,
        split_id=split_id,
    )

    if split is None:
        return None

    if (
        split.source != "USER"
        or split.owner_id != user_id
    ):
        raise PermissionError(
            "You do not have permission to modify this split"
        )

    return split


def update_user_split(
    db: Session,
    user_id: int,
    split_id: int,
    data: SplitUpdate,
) -> Split | None:
    split = get_owned_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(split, field, value)

    return update_split(
        db=db,
        split=split,
    )


def delete_user_split(
    db: Session,
    user_id: int,
    split_id: int,
) -> bool:
    split = get_owned_split(
        db=db,
        user_id=user_id,
        split_id=split_id,
    )

    if split is None:
        return False

    try:
        delete_split(
            db=db,
            split=split,
        )

    except IntegrityError as exc:
        db.rollback()

        raise ValueError(
            "Split is being used by a training plan and cannot be deleted"
        ) from exc

    return True