from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    sets: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    reps: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    distance_meters: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    load_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    intensity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    rest_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    tempo: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    workout = relationship("Workout")
    exercise = relationship("Exercise")