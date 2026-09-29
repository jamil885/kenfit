from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    goal: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    duration_weeks: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    split_id: Mapped[int] = mapped_column(
        ForeignKey("splits.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="USER",
    )

    split = relationship("Split")
    owner = relationship("User")