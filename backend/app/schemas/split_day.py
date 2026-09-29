from pydantic import BaseModel, ConfigDict, Field


class SplitDayCreate(BaseModel):
    workout_id: int | None = None

    order: int = Field(
        ge=1,
    )

    name: str | None = Field(
        default=None,
        max_length=100,
    )


class SplitDayUpdate(BaseModel):
    workout_id: int | None = None

    order: int | None = Field(
        default=None,
        ge=1,
    )

    name: str | None = Field(
        default=None,
        max_length=100,
    )


class SplitDayResponse(BaseModel):
    id: int
    split_id: int
    workout_id: int | None

    order: int
    name: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )