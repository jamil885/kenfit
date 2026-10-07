from datetime import date, datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from app.schemas.common import Schema, not_future


class Prescription(Schema):
    exercise_id: int = Field(gt=0)
    position: int = Field(ge=1, le=100)
    sets: int | None = Field(default=None, ge=1, le=100)
    reps: int | None = Field(default=None, ge=1, le=10000)
    duration_seconds: int | None = Field(default=None, gt=0, le=86400)
    distance_meters: float | None = Field(default=None, gt=0, le=1000000)
    weight_kg: float | None = Field(default=None, ge=0, le=2000)
    rest_seconds: int | None = Field(default=None, ge=0, le=7200)
    intensity: str | None = Field(default=None, max_length=50)
    tempo: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)
    progression: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def work_required(self):
        if not any((self.reps, self.duration_seconds, self.distance_meters)):
            raise ValueError("Specify reps, duration or distance")
        return self


class ContentCreate(Schema):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=4000)


class WorkoutCreate(ContentCreate):
    discipline: str = Field(min_length=2, max_length=50)
    exercises: list[Prescription] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_positions(self):
        if len({x.position for x in self.exercises}) != len(self.exercises):
            raise ValueError("Duplicate exercise positions")
        return self


class ContentResponse(Schema):
    id: int
    name: str
    description: str | None
    owner_id: int | None
    source: str
    visibility: str
    parent_id: int | None
    is_active: bool
    created_at: datetime


class WorkoutResponse(ContentResponse):
    discipline: str
    exercises: list[Prescription]


class SplitDayCreate(Schema):
    day: int = Field(ge=1, le=28)
    workout_id: int | None = Field(default=None, gt=0)
    label: str | None = Field(default=None, max_length=100)


class SplitCreate(ContentCreate):
    cycle_days: int = Field(default=7, ge=1, le=28)
    days: list[SplitDayCreate] = Field(min_length=1, max_length=28)

    @model_validator(mode="after")
    def valid_days(self):
        if len({x.day for x in self.days}) != len(self.days) or any(
            x.day > self.cycle_days for x in self.days
        ):
            raise ValueError("Split days must be unique and within the cycle")
        return self


class SplitResponse(ContentResponse):
    cycle_days: int
    days: list[SplitDayCreate]


class PlanDayCreate(Schema):
    week: int = Field(ge=1, le=52)
    day: int = Field(ge=1, le=7)
    workout_id: int = Field(gt=0)
    phase: str | None = Field(default=None, max_length=50)


class TrainingPlanCreate(ContentCreate):
    weeks: int = Field(ge=1, le=52)
    goal: str = Field(min_length=2, max_length=50)
    split_id: int | None = Field(default=None, gt=0)
    schedule: list[PlanDayCreate] = Field(min_length=1, max_length=364)

    @model_validator(mode="after")
    def valid_schedule(self):
        if len({(x.week, x.day) for x in self.schedule}) != len(self.schedule) or any(
            x.week > self.weeks for x in self.schedule
        ):
            raise ValueError("Schedule must be unique and within plan weeks")
        return self


class TrainingPlanResponse(ContentResponse):
    weeks: int
    goal: str
    split_id: int | None
    schedule: list[PlanDayCreate]


class ResultCreate(Schema):
    position: int = Field(ge=1)
    set_number: int = Field(ge=1, le=100)
    reps: int | None = Field(default=None, ge=0, le=10000)
    weight_kg: float | None = Field(default=None, ge=0, le=2000)
    duration_seconds: int | None = Field(default=None, ge=0, le=86400)
    distance_meters: float | None = Field(default=None, ge=0, le=1000000)
    rpe: float | None = Field(default=None, ge=1, le=10)

    @model_validator(mode="after")
    def result_required(self):
        if all(x is None for x in (self.reps, self.duration_seconds, self.distance_meters)):
            raise ValueError("Specify a performed result")
        return self


class WorkoutLogCreate(Schema):
    workout_id: int = Field(gt=0)
    performed_on: date
    status: Literal["completed", "partial", "skipped"] = "completed"
    duration_seconds: int | None = Field(default=None, gt=0, le=86400)
    notes: str | None = Field(default=None, max_length=2000)
    results: list[ResultCreate] = Field(default_factory=list, max_length=1000)
    _date = field_validator("performed_on")(not_future)

    @model_validator(mode="after")
    def validate_results(self):
        if len({(x.position, x.set_number) for x in self.results}) != len(self.results):
            raise ValueError("Duplicate set results")
        if self.status == "skipped" and self.results:
            raise ValueError("Skipped workouts cannot have results")
        if self.status != "skipped" and not self.results:
            raise ValueError("Completed or partial workouts require results")
        return self


class ResultResponse(ResultCreate):
    exercise_id: int
    exercise_name: str
    prescribed_sets: int | None
    prescribed_reps: int | None
    prescribed_weight_kg: float | None
    prescribed_duration_seconds: int | None
    prescribed_distance_meters: float | None


class WorkoutLogResponse(Schema):
    id: int
    workout_id: int
    workout_name: str
    performed_on: date
    status: str
    duration_seconds: int | None
    notes: str | None
    results: list[ResultResponse]


class WeightCreate(Schema):
    recorded_on: date
    weight_kg: float = Field(gt=0, le=500)
    _date = field_validator("recorded_on")(not_future)


class WeightResponse(WeightCreate):
    id: int


class GenerateRequest(Schema):
    days_per_week: int | None = Field(default=None, ge=1, le=6)
    weeks: int = Field(default=4, ge=1, le=12)
    equipment: list[str] | None = Field(default=None, max_length=20)
    discipline: Literal["strength", "running", "mobility"] | None = None


class ProgressionRequest(Schema):
    log_id: int = Field(gt=0)
