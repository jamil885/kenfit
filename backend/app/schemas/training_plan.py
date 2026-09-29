from pydantic import BaseModel, ConfigDict, Field


class TrainingPlanCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )

    description: str | None = None

    goal: str | None = Field(
        default=None,
        max_length=100,
    )

    duration_weeks: int | None = Field(
        default=None,
        ge=1,
    )

    split_id: int


class TrainingPlanUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    description: str | None = None

    goal: str | None = Field(
        default=None,
        max_length=100,
    )

    duration_weeks: int | None = Field(
        default=None,
        ge=1,
    )

    split_id: int | None = None


class TrainingPlanResponse(BaseModel):
    id: int
    name: str
    description: str | None
    goal: str | None
    duration_weeks: int | None

    split_id: int
    owner_id: int | None
    source: str

    model_config = ConfigDict(
        from_attributes=True,
    )