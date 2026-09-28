from datetime import datetime

from pydantic import BaseModel, Field


class ExerciseMuscleCreate(BaseModel):
    muscle_group_id: int
    role: str = Field(min_length=1, max_length=20)


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None

    discipline: str = Field(min_length=2, max_length=50)
    modality: str | None = Field(default=None, max_length=50)
    exercise_type: str = Field(min_length=2, max_length=50)

    equipment: str | None = Field(default=None, max_length=100)
    difficulty: str | None = Field(default=None, max_length=30)

    instructions: str | None = None

    muscle_groups: list[ExerciseMuscleCreate] = Field(
    default_factory=list
)


class ExerciseUpdate(BaseModel):
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


class ExerciseMuscleResponse(BaseModel):
    muscle_group_id: int
    role: str

    model_config = {
        "from_attributes": True,
    }


class ExerciseResponse(BaseModel):
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

    muscle_groups: list[ExerciseMuscleResponse] = Field(
    default_factory=list
)

    model_config = {
        "from_attributes": True,
    }