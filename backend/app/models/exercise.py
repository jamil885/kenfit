from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    discipline: Mapped[str] = mapped_column(
        ForeignKey("disciplines.code"),
        nullable=False,
    )

    modality: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    exercise_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    equipment: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    difficulty: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[str] = mapped_column(String(20), default="USER", nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), default="private", nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("exercises.id"))

    muscle_groups = relationship(
        "ExerciseMuscle",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
