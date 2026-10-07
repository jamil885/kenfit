"""Normalized prescriptions, reusable templates and immutable execution snapshots."""

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def now():
    return datetime.now(timezone.utc)


class Content:
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[str] = mapped_column(String(20), default="USER")
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Workout(Content, Base):
    __tablename__ = "workouts"
    discipline: Mapped[str] = mapped_column(String(50))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id"))
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        cascade="all, delete-orphan", order_by="WorkoutExercise.position"
    )


class Prescription:
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    distance_meters: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    rest_seconds: Mapped[int | None] = mapped_column(Integer)
    intensity: Mapped[str | None] = mapped_column(String(50))
    tempo: Mapped[str | None] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text)


class WorkoutExercise(Prescription, Base):
    __tablename__ = "workout_exercises"
    __table_args__ = (UniqueConstraint("workout_id", "position", name="uq_workout_position"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    progression: Mapped[str | None] = mapped_column(String(100))


class Split(Content, Base):
    __tablename__ = "splits"
    cycle_days: Mapped[int] = mapped_column(Integer, default=7)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("splits.id"))
    days: Mapped[list["SplitDay"]] = relationship(
        cascade="all, delete-orphan", order_by="SplitDay.day"
    )


class SplitDay(Base):
    __tablename__ = "split_days"
    __table_args__ = (UniqueConstraint("split_id", "day", name="uq_split_day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    split_id: Mapped[int] = mapped_column(ForeignKey("splits.id", ondelete="CASCADE"), index=True)
    day: Mapped[int] = mapped_column(Integer)
    workout_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id"))
    label: Mapped[str | None] = mapped_column(String(100))


class TrainingPlan(Content, Base):
    __tablename__ = "training_plans"
    weeks: Mapped[int] = mapped_column(Integer)
    goal: Mapped[str] = mapped_column(String(50))
    split_id: Mapped[int | None] = mapped_column(ForeignKey("splits.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("training_plans.id"))
    schedule: Mapped[list["PlanDay"]] = relationship(
        cascade="all, delete-orphan", order_by="PlanDay.week, PlanDay.day"
    )


class PlanDay(Base):
    __tablename__ = "plan_days"
    __table_args__ = (UniqueConstraint("plan_id", "week", "day", name="uq_plan_day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("training_plans.id", ondelete="CASCADE"), index=True
    )
    week: Mapped[int] = mapped_column(Integer)
    day: Mapped[int] = mapped_column(Integer)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"))
    phase: Mapped[str | None] = mapped_column(String(50))


class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"), index=True)
    workout_name: Mapped[str] = mapped_column(String(100))
    performed_on: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    results: Mapped[list["SetResult"]] = relationship(
        cascade="all, delete-orphan", order_by="SetResult.id"
    )


class SetResult(Base):
    __tablename__ = "set_results"
    __table_args__ = (UniqueConstraint("log_id", "position", "set_number", name="uq_log_set"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    log_id: Mapped[int] = mapped_column(
        ForeignKey("workout_logs.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    exercise_name: Mapped[str] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(Integer)
    set_number: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    distance_meters: Mapped[float | None] = mapped_column(Float)
    rpe: Mapped[float | None] = mapped_column(Float)
    prescribed_sets: Mapped[int | None] = mapped_column(Integer)
    prescribed_reps: Mapped[int | None] = mapped_column(Integer)
    prescribed_weight_kg: Mapped[float | None] = mapped_column(Float)
    prescribed_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    prescribed_distance_meters: Mapped[float | None] = mapped_column(Float)


class WeightEntry(Base):
    __tablename__ = "weight_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_on", name="uq_weight_day"),
        CheckConstraint("weight_kg > 0", name="ck_positive_weight"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    recorded_on: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[float] = mapped_column(Float)
