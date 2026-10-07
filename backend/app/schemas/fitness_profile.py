from datetime import date
from typing import ClassVar

from pydantic import Field, field_validator

from app.schemas.common import Patch, Schema


def valid_birth(value):
    if value >= date.today():
        raise ValueError("Birth date must be in the past")
    return value


class FitnessProfileCreate(Schema):
    birth_date: date
    _birth = field_validator("birth_date")(valid_birth)
    gender: str = Field(min_length=1, max_length=50)
    height_cm: float = Field(ge=50, le=250)
    weight_kg: float = Field(ge=20, le=500)
    fitness_level: str = Field(min_length=1, max_length=30)
    goal: str = Field(min_length=1, max_length=50)

    days_per_week: int = Field(default=3, ge=1, le=6)
    session_minutes: int = Field(default=45, ge=10, le=180)
    available_equipment: list[str] = Field(default_factory=lambda: ["bodyweight"], max_length=20)
    preferred_discipline: str = Field(default="strength", min_length=2, max_length=50)


class FitnessProfileUpdate(Patch):
    required_non_null: ClassVar = (
        "birth_date",
        "gender",
        "height_cm",
        "weight_kg",
        "fitness_level",
        "goal",
        "days_per_week",
        "session_minutes",
        "available_equipment",
        "preferred_discipline",
    )
    birth_date: date | None = None
    _birth = field_validator("birth_date")(valid_birth)
    gender: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    height_cm: float | None = Field(
        default=None,
        ge=50,
        le=250,
    )
    weight_kg: float | None = Field(
        default=None,
        ge=20,
        le=500,
    )
    fitness_level: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )
    goal: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    days_per_week: int | None = Field(default=None, ge=1, le=6)
    session_minutes: int | None = Field(default=None, ge=10, le=180)
    available_equipment: list[str] | None = Field(default=None, max_length=20)
    preferred_discipline: str | None = Field(default=None, min_length=2, max_length=50)


class FitnessProfileResponse(Schema):
    id: int
    user_id: int
    birth_date: date
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: str
    goal: str

    model_config = {"from_attributes": True}

    days_per_week: int
    session_minutes: int
    available_equipment: list[str]
    preferred_discipline: str
