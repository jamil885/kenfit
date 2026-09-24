from datetime import date

from pydantic import BaseModel, Field


class FitnessProfileCreate(BaseModel):
    birth_date: date
    gender: str = Field(min_length=1, max_length=50)
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    fitness_level: str = Field(min_length=1, max_length=30)
    goal: str = Field(min_length=1, max_length=50)


class FitnessProfileResponse(BaseModel):
    id: int
    user_id: int
    birth_date: date
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: str
    goal: str

    model_config = {
        "from_attributes": True
    }