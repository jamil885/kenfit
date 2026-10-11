from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrainingSessionCreate(BaseModel):
    workout_id: int | None = None
    training_plan_id: int | None = None
    notes: str | None = None


class TrainingSessionUpdate(BaseModel):
    notes: str | None = None


class TrainingSessionResponse(BaseModel):
    id: int
    user_id: int
    workout_id: int | None
    training_plan_id: int | None
    started_at: datetime
    finished_at: datetime | None
    status: str
    notes: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )
