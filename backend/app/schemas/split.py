from pydantic import BaseModel, ConfigDict, Field


class SplitCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )

    description: str | None = None


class SplitUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    description: str | None = None


class SplitResponse(BaseModel):
    id: int
    name: str
    description: str | None

    owner_id: int | None
    source: str

    model_config = ConfigDict(
        from_attributes=True,
    )
    