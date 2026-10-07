from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ExerciseMuscle(Base):
    __tablename__ = "exercise_muscles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    exercise = relationship(
        "Exercise",
        back_populates="muscle_groups",
    )

    muscle_group = relationship(
        "MuscleGroup",
        back_populates="exercises",
    )
