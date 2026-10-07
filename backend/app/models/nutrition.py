from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Food(Base):
    __tablename__ = "foods"
    __table_args__ = (
        CheckConstraint(
            "calories >= 0 AND protein_g >= 0 AND carbs_g >= 0 AND fat_g >= 0",
            name="ck_food_macros",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[str] = mapped_column(String(20), default="USER")
    calories: Mapped[float] = mapped_column(Float)
    protein_g: Mapped[float] = mapped_column(Float)
    carbs_g: Mapped[float] = mapped_column(Float)
    fat_g: Mapped[float] = mapped_column(Float)
    serving_grams: Mapped[float | None] = mapped_column(Float)
    reference: Mapped[str | None] = mapped_column(String(255))


class NutritionTarget(Base):
    __tablename__ = "nutrition_targets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    calories: Mapped[float] = mapped_column(Float)
    protein_g: Mapped[float] = mapped_column(Float)
    carbs_g: Mapped[float] = mapped_column(Float)
    fat_g: Mapped[float] = mapped_column(Float)


class MealEntry(Base):
    __tablename__ = "meal_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"))
    food_name: Mapped[str] = mapped_column(String(100))
    recorded_on: Mapped[date] = mapped_column(Date, index=True)
    meal: Mapped[str] = mapped_column(String(20))
    grams: Mapped[float] = mapped_column(Float)
    calories: Mapped[float] = mapped_column(Float)
    protein_g: Mapped[float] = mapped_column(Float)
    carbs_g: Mapped[float] = mapped_column(Float)
    fat_g: Mapped[float] = mapped_column(Float)
