from datetime import date
from typing import Literal

from pydantic import Field, field_validator, model_validator

from app.schemas.common import Schema, not_future


class Macros(Schema):
    calories: float = Field(ge=0, le=10000)
    protein_g: float = Field(ge=0, le=1000)
    carbs_g: float = Field(ge=0, le=2000)
    fat_g: float = Field(ge=0, le=1000)


class FoodCreate(Macros):
    name: str = Field(min_length=2, max_length=100)
    serving_grams: float | None = Field(default=None, gt=0, le=10000)
    reference: str | None = Field(default=None, max_length=255)


class FoodResponse(FoodCreate):
    id: int
    source: str
    owner_id: int | None


class TargetCreate(Macros):
    @model_validator(mode="after")
    def energy_consistent(self):
        energy = 4 * (self.protein_g + self.carbs_g) + 9 * self.fat_g
        if self.calories < 500 or abs(energy - self.calories) > self.calories * 0.1:
            raise ValueError("Calories must be >=500 and agree with macros within 10%")
        return self


class EstimateRequest(Schema):
    equation_sex: Literal["male", "female"]
    activity_factor: float = Field(ge=1.2, le=1.9)
    calorie_adjustment: int = Field(default=0, ge=-500, le=500)


class MealCreate(Schema):
    food_id: int = Field(gt=0)
    recorded_on: date
    meal: Literal["breakfast", "lunch", "dinner", "snack"]
    grams: float | None = Field(default=None, gt=0, le=10000)
    servings: float | None = Field(default=None, gt=0, le=100)
    _date = field_validator("recorded_on")(not_future)

    @model_validator(mode="after")
    def quantity(self):
        if (self.grams is None) == (self.servings is None):
            raise ValueError("Specify exactly one of grams or servings")
        return self


class MealResponse(Macros):
    id: int
    food_id: int
    food_name: str
    recorded_on: date
    meal: str
    grams: float


class DaySummary(Schema):
    recorded_on: date
    consumed: Macros
    target: Macros | None
    remaining: dict[str, float] | None
    entries: list[MealResponse]
