"""Idempotent demo catalog. Run after migrations: python -m app.seed."""

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import (
    Exercise,
    Food,
    MuscleGroup,
    PlanDay,
    Split,
    SplitDay,
    TrainingPlan,
    Workout,
    WorkoutExercise,
)

EXERCISES = [
    (
        "Bodyweight squat",
        "strength",
        "bodyweight",
        "Bend hips and knees, keep balance and move in a comfortable range.",
    ),
    (
        "Incline push-up",
        "strength",
        "bodyweight",
        "Use a stable elevated surface and keep your trunk aligned.",
    ),
    (
        "Glute bridge",
        "strength",
        "bodyweight",
        "Lie supine, bend knees and raise hips without arching your back.",
    ),
    (
        "Bird dog",
        "strength",
        "bodyweight",
        "From hands and knees, slowly extend opposite arm and leg.",
    ),
    ("Easy run", "running", "none", "Run at a comfortable conversational pace; walk as needed."),
    ("Hip mobility", "mobility", "none", "Move hips slowly within a comfortable range."),
    (
        "Shoulder mobility",
        "mobility",
        "none",
        "Use controlled shoulder circles without forcing the range.",
    ),
]
# Representative demo values per 100g; not a verified production nutrition database.
FOODS = [
    ("White rice, cooked", 130, 2.7, 28.2, 0.3, 150),
    ("Chicken breast, cooked", 165, 31, 0, 3.6, 100),
    ("Banana, raw", 89, 1.1, 22.8, 0.3, 100),
    ("Egg, cooked", 155, 12.6, 1.1, 10.6, 50),
    ("Oats, dry", 379, 13.2, 67.7, 6.5, 40),
    ("Black beans, cooked", 132, 8.9, 23.7, 0.5, 100),
]


def seed(db):
    from app.services.discipline import ensure_discipline

    for code in (
        "strength",
        "hypertrophy",
        "power",
        "endurance",
        "running",
        "cycling",
        "calisthenics",
        "weightlifting",
        "conditioning",
        "mobility",
        "hybrid",
    ):
        ensure_discipline(db, code)
    for name in ("quadriceps", "hamstrings", "glutes", "chest", "back", "shoulders", "core"):
        if db.scalar(select(MuscleGroup).where(MuscleGroup.name == name)) is None:
            db.add(MuscleGroup(name=name))
    for name, discipline, equipment, instructions in EXERCISES:
        if (
            db.scalar(select(Exercise).where(Exercise.name == name, Exercise.source == "SYSTEM"))
            is None
        ):
            db.add(
                Exercise(
                    name=name,
                    discipline=discipline,
                    exercise_type="movement" if discipline == "strength" else discipline,
                    equipment=equipment,
                    difficulty="beginner",
                    instructions=instructions,
                    owner_id=None,
                    source="SYSTEM",
                    visibility="platform",
                )
            )
    for name, kcal, protein, carbs, fat, serving in FOODS:
        if db.scalar(select(Food).where(Food.name == name, Food.source == "SYSTEM")) is None:
            db.add(
                Food(
                    name=name,
                    calories=kcal,
                    protein_g=protein,
                    carbs_g=carbs,
                    fat_g=fat,
                    serving_grams=serving,
                    owner_id=None,
                    source="SYSTEM",
                    reference="Demo approximate values; verify against food label or USDA before production",
                )
            )
    db.flush()
    workout = db.scalar(
        select(Workout).where(Workout.name == "KenFit Full Body", Workout.source == "SYSTEM")
    )
    if workout is None:
        exercises = [
            db.scalar(select(Exercise).where(Exercise.name == name, Exercise.source == "SYSTEM"))
            for name, _, _, _ in EXERCISES[:4]
        ]
        workout = Workout(
            name="KenFit Full Body",
            discipline="strength",
            source="SYSTEM",
            visibility="platform",
            owner_id=None,
            exercises=[
                WorkoutExercise(exercise_id=e.id, position=i + 1, sets=2, reps=8, rest_seconds=90)
                for i, e in enumerate(exercises)
            ],
        )
        db.add(workout)
        db.flush()
    split = db.scalar(
        select(Split).where(Split.name == "KenFit Full Body 3 days", Split.source == "SYSTEM")
    )
    if split is None:
        split = Split(
            name="KenFit Full Body 3 days",
            cycle_days=7,
            source="SYSTEM",
            visibility="platform",
            owner_id=None,
            days=[SplitDay(day=d, workout_id=workout.id) for d in (1, 3, 5)],
        )
        db.add(split)
        db.flush()
    if (
        db.scalar(
            select(TrainingPlan).where(
                TrainingPlan.name == "KenFit 4-week starter", TrainingPlan.source == "SYSTEM"
            )
        )
        is None
    ):
        db.add(
            TrainingPlan(
                name="KenFit 4-week starter",
                weeks=4,
                goal="general_fitness",
                split_id=split.id,
                source="SYSTEM",
                visibility="platform",
                owner_id=None,
                schedule=[
                    PlanDay(week=w, day=d, workout_id=workout.id, phase="base")
                    for w in range(1, 5)
                    for d in (1, 3, 5)
                ],
            )
        )
    db.commit()


if __name__ == "__main__":
    with SessionLocal() as db:
        seed(db)
    print("Starter catalogs installed. Re-running does not duplicate entries.")
