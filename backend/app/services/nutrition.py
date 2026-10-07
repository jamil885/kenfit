from datetime import date

from fastapi import HTTPException
from sqlalchemy import or_, select

from app.models.fitness_profile import FitnessProfile
from app.models.nutrition import Food, MealEntry, NutritionTarget
from app.services.content import save

MACROS = ("calories", "protein_g", "carbs_g", "fat_g")


def get_food(db, food_id, user_id):
    obj = db.scalar(
        select(Food).where(
            Food.id == food_id, or_(Food.owner_id == user_id, Food.source == "SYSTEM")
        )
    )
    if obj is None:
        raise HTTPException(404, "Food not found")
    return obj


def list_foods(db, user_id, offset=0, limit=50, search=None):
    stmt = select(Food).where(or_(Food.owner_id == user_id, Food.source == "SYSTEM"))
    if search:
        stmt = stmt.where(
            Food.name.ilike("%" + search.replace("%", "\\%").replace("_", "\\_") + "%", escape="\\")
        )
    return list(db.scalars(stmt.order_by(Food.id).offset(offset).limit(limit)))


def create_food(db, data, user_id):
    return save(db, Food(**data.model_dump(), owner_id=user_id, source="USER"))


def update_food(db, food_id, data, user_id):
    obj = get_food(db, food_id, user_id)
    if obj.owner_id != user_id or obj.source != "USER":
        raise HTTPException(403, "Platform food is read only")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    return save(db, obj)


def get_target(db, user_id):
    return db.scalar(select(NutritionTarget).where(NutritionTarget.user_id == user_id))


def set_target(db, data, user_id):
    obj = get_target(db, user_id)
    if obj is None:
        obj = NutritionTarget(user_id=user_id, **data.model_dump())
    else:
        for k, v in data.model_dump().items():
            setattr(obj, k, v)
    return save(db, obj)


def estimate(db, data, user_id):
    profile = db.scalar(select(FitnessProfile).where(FitnessProfile.user_id == user_id))
    if profile is None:
        raise HTTPException(409, "Create a fitness profile first")
    today = date.today()
    age = (
        today.year
        - profile.birth_date.year
        - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))
    )
    if not 18 <= age <= 80:
        raise HTTPException(422, "This estimate is limited to adults aged 18–80")
    bmr = (
        10 * profile.weight_kg
        + 6.25 * profile.height_cm
        - 5 * age
        + (5 if data.equation_sex == "male" else -161)
    )
    calories = round(bmr * data.activity_factor + data.calorie_adjustment)
    if calories < 1200 or calories > 5000:
        raise HTTPException(
            422, "Estimate is outside the supported range; set a reviewed target manually"
        )
    # MVP configurable macro allocation, not a clinical prescription.
    protein = round(calories * 0.25 / 4, 1)
    fat = round(calories * 0.30 / 9, 1)
    carbs = round((calories - 4 * protein - 9 * fat) / 4, 1)
    return {
        "calories": calories,
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat,
        "resting_energy_estimate": round(bmr),
        "method": "Mifflin–St Jeor",
        "notice": "General estimate for healthy adults; review and explicitly save targets. Not suitable for pregnancy or medical dietary management.",
    }


def create_meal(db, data, user_id):
    food = get_food(db, data.food_id, user_id)
    if data.servings is not None and food.serving_grams is None:
        raise HTTPException(422, "This food has no defined serving; use grams")
    grams = data.grams if data.grams is not None else data.servings * food.serving_grams
    if grams > 10000:
        raise HTTPException(422, "Quantity exceeds 10000 grams")
    obj = MealEntry(
        user_id=user_id,
        food_id=food.id,
        food_name=food.name,
        recorded_on=data.recorded_on,
        meal=data.meal,
        grams=grams,
        **{k: round(getattr(food, k) * grams / 100, 3) for k in MACROS},
    )
    return save(db, obj)


def day_summary(db, user_id, day):
    entries = list(
        db.scalars(
            select(MealEntry)
            .where(MealEntry.user_id == user_id, MealEntry.recorded_on == day)
            .order_by(MealEntry.id)
        )
    )
    consumed = {k: round(sum(getattr(x, k) for x in entries), 3) for k in MACROS}
    target = get_target(db, user_id)
    remaining = {k: round(getattr(target, k) - consumed[k], 3) for k in MACROS} if target else None
    return {
        "recorded_on": day,
        "consumed": consumed,
        "target": target,
        "remaining": remaining,
        "entries": entries,
    }
