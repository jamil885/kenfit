from datetime import datetime
from typing import ClassVar, Literal

from pydantic import Field

from app.schemas.common import Patch, Schema


class ExerciseMuscleCreate(Schema):
    muscle_group_id: int
    role: Literal["primary", "secondary"] = "primary"


class ExerciseCreate(Schema):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None

    discipline: str = Field(min_length=2, max_length=50)
    modality: str | None = Field(default=None, max_length=50)
    exercise_type: str = Field(min_length=2, max_length=50)

    equipment: str | None = Field(default=None, max_length=100)
    difficulty: str | None = Field(default=None, max_length=30)

    instructions: str | None = None

    muscle_groups: list[ExerciseMuscleCreate] = Field(default_factory=list)


class ExerciseUpdate(Patch):
    required_non_null: ClassVar = ("name", "discipline", "exercise_type", "muscle_groups")
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None

    discipline: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    modality: str | None = Field(
        default=None,
        max_length=50,
    )

    exercise_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    equipment: str | None = Field(
        default=None,
        max_length=100,
    )

    difficulty: str | None = Field(
        default=None,
        max_length=30,
    )

    instructions: str | None = None

    muscle_groups: list[ExerciseMuscleCreate] | None = None


class ExerciseMuscleResponse(Schema):
    muscle_group_id: int
    role: str

    model_config = {
        "from_attributes": True,
    }


class ExerciseResponse(Schema):
    owner_id: int | None
    source: str
    visibility: str
    parent_id: int | None
    id: int

    name: str
    description: str | None

    discipline: str
    modality: str | None
    exercise_type: str

    equipment: str | None
    difficulty: str | None
    instructions: str | None

    is_active: bool
    created_at: datetime

    muscle_groups: list[ExerciseMuscleResponse] = Field(default_factory=list)

    model_config = {
        "from_attributes": True,
    }
