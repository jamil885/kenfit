from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FitnessProfile(Base):
    __tablename__ = "fitness_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    birth_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    height_cm: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    weight_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fitness_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    goal: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )