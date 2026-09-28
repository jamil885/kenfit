from pydantic import BaseModel, ConfigDict, Field


class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    order: int = Field(ge=1)

    sets: int | None = Field(default=None, ge=1)
    reps: int | None = Field(default=None, ge=1)

    duration_seconds: int | None = Field(default=None, ge=1)
    distance_meters: float | None = Field(default=None, ge=0)
    load_kg: float | None = Field(default=None, ge=0)

    intensity: str | None = None
    rest_seconds: int | None = Field(default=None, ge=0)
    tempo: str | None = None
    notes: str | None = None


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutExerciseResponse(WorkoutExerciseBase):
    id: int
    workout_id: int

    model_config = ConfigDict(from_attributes=True)