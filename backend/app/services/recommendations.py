from fastapi import HTTPException
from sqlalchemy import select

from app.engine.progression import suggest
from app.engine.workout_generator import build_plan, build_split, build_workouts
from app.models.exercise import Exercise
from app.models.fitness_profile import FitnessProfile
from app.models.training import Split, TrainingPlan, Workout, WorkoutLog
from app.repositories.content import list_content
from app.services.training import create_content, user_record

STRENGTH_NAMES = ["Bodyweight squat", "Incline push-up", "Glute bridge", "Bird dog"]


def generate(db, request, user_id):
    profile = db.scalar(select(FitnessProfile).where(FitnessProfile.user_id == user_id))
    if profile is None:
        raise HTTPException(409, "Create a fitness profile first")
    from app.schemas.training import GenerateRequest

    if request.discipline is None and profile.preferred_discipline not in (
        "strength",
        "running",
        "mobility",
    ):
        raise HTTPException(
            422,
            "Automatic starter generation supports strength, running and mobility; use custom workouts for other disciplines",
        )
    request = GenerateRequest(
        days_per_week=request.days_per_week or profile.days_per_week,
        weeks=request.weeks,
        equipment=request.equipment
        if request.equipment is not None
        else profile.available_equipment,
        discipline=request.discipline or profile.preferred_discipline,
    )
    # MVP supports reviewed starter templates; broader custom disciplines use CRUD.
    equipment = {x.strip().lower() for x in request.equipment} | {"bodyweight", "none"}
    available = list_content(db, Exercise, user_id, limit=100)
    candidates = [
        e
        for e in available
        if e.discipline == request.discipline and (e.equipment or "none").lower() in equipment
    ]
    preferred = {
        "strength": STRENGTH_NAMES,
        "running": ["Easy run"],
        "mobility": ["Hip mobility", "Shoulder mobility"],
    }[request.discipline]
    selected = []
    for name in preferred:
        match = next((e for e in candidates if e.name == name and e.source == "SYSTEM"), None)
        if match is None:
            raise HTTPException(409, "Run the seed command to install the starter catalog")
        selected.append(match)
    if request.discipline == "strength" and request.days_per_week > 3:
        raise HTTPException(
            422, "The full-body starter supports 1–3 days; use custom splits for higher frequencies"
        )
    try:
        workouts = [
            create_content(db, Workout, data, user_id, commit=False)
            for data in build_workouts(
                request, selected, profile.fitness_level, profile.session_minutes, profile.goal
            )
        ]
        split = create_content(db, Split, build_split(request, workouts), user_id, commit=False)
        plan = create_content(
            db, TrainingPlan, build_plan(request, split, profile.goal), user_id, commit=False
        )
        db.commit()
        db.refresh(plan)
        return plan
    except Exception:
        db.rollback()
        raise


def progression(db, log_id, user_id):
    return suggest(user_record(db, WorkoutLog, log_id, user_id))
