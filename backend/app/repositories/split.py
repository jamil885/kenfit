from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.split import Split


def create_split(
    db: Session,
    name: str,
    description: str | None,
    owner_id: int | None,
    source: str,
) -> Split:
    split = Split(
        name=name,
        description=description,
        owner_id=owner_id,
        source=source,
    )

    db.add(split)
    db.commit()
    db.refresh(split)

    return split


def get_split_by_id(
    db: Session,
    split_id: int,
) -> Split | None:
    statement = select(Split).where(
        Split.id == split_id
    )

    return db.scalar(statement)


def get_splits_for_user(
    db: Session,
    user_id: int,
) -> list[Split]:
    statement = (
        select(Split)
        .where(
            or_(
                Split.source == "SYSTEM",
                Split.owner_id == user_id,
            )
        )
        .order_by(Split.id)
    )

    return list(
        db.scalars(statement).all()
    )


def update_split(
    db: Session,
    split: Split,
) -> Split:
    db.commit()
    db.refresh(split)

    return split


def delete_split(
    db: Session,
    split: Split,
) -> None:
    db.delete(split)
    db.commit()