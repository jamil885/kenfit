from pydantic import BaseModel, ConfigDict, Field

from app.schemas.workout_exercise import WorkoutExerciseResponse


class WorkoutBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class WorkoutResponse(WorkoutBase):
    id: int
    owner_id: int | None
    source: str

    model_config = ConfigDict(from_attributes=True)


class WorkoutDetailResponse(WorkoutResponse):
    exercises: list[WorkoutExerciseResponse] = []