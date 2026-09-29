from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.split_day import SplitDay


def create_split_day(
    db: Session,
    split_id: int,
    workout_id: int | None,
    order: int,
    name: str | None,
) -> SplitDay:
    split_day = SplitDay(
        split_id=split_id,
        workout_id=workout_id,
        order=order,
        name=name,
    )

    db.add(split_day)
    db.commit()
    db.refresh(split_day)

    return split_day


def get_split_day_by_id(
    db: Session,
    split_day_id: int,
) -> SplitDay | None:
    statement = select(SplitDay).where(
        SplitDay.id == split_day_id
    )

    return db.scalar(statement)


def get_split_days(
    db: Session,
    split_id: int,
) -> list[SplitDay]:
    statement = (
        select(SplitDay)
        .where(
            SplitDay.split_id == split_id
        )
        .order_by(SplitDay.order)
    )

    return list(
        db.scalars(statement).all()
    )


def update_split_day(
    db: Session,
    split_day: SplitDay,
) -> SplitDay:
    db.commit()
    db.refresh(split_day)

    return split_day


def delete_split_day(
    db: Session,
    split_day: SplitDay,
) -> None:
    db.delete(split_day)
    db.commit()