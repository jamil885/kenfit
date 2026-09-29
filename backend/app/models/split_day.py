from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SplitDay(Base):
    __tablename__ = "split_days"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    split_id: Mapped[int] = mapped_column(
        ForeignKey("splits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    workout_id: Mapped[int | None] = mapped_column(
        ForeignKey("workouts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    split = relationship(
    "Split",
    back_populates="days",
)
    workout = relationship("Workout")