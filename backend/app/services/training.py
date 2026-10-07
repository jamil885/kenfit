from fastapi import HTTPException
from sqlalchemy import select

from app.models.exercise import Exercise
from app.models.training import (
    PlanDay,
    SetResult,
    Split,
    SplitDay,
    TrainingPlan,
    WeightEntry,
    Workout,
    WorkoutExercise,
    WorkoutLog,
)
from app.schemas.training import SplitCreate, TrainingPlanCreate, WorkoutCreate
from app.services.content import owned, readable, save

CONFIG = {
    Workout: ("exercises", WorkoutExercise, Exercise, "exercise_id"),
    Split: ("days", SplitDay, Workout, "workout_id"),
    TrainingPlan: ("schedule", PlanDay, Workout, "workout_id"),
}


def validate_links(db, model, data, user_id):
    attr, child, reference, field = CONFIG[model]
    for entry in getattr(data, attr):
        link = getattr(entry, field)
        if link is not None:
            readable(db, reference, link, user_id)
    if model is TrainingPlan and data.split_id is not None:
        readable(db, Split, data.split_id, user_id)


def create_content(db, model, data, user_id, commit=True):
    validate_links(db, model, data, user_id)
    attr, child, _, _ = CONFIG[model]
    obj = model(
        **data.model_dump(exclude={attr}), owner_id=user_id, source="USER", visibility="private"
    )
    setattr(obj, attr, [child(**x.model_dump()) for x in getattr(data, attr)])
    db.add(obj)
    if commit:
        return save(db, obj)
    db.flush()
    return obj


def replace_content(db, model, content_id, data, user_id):
    obj = owned(db, model, content_id, user_id)
    validate_links(db, model, data, user_id)
    attr, child, _, _ = CONFIG[model]
    # Delete old prescriptions before inserting identical ordered slots.
    getattr(obj, attr).clear()
    db.flush()
    for k, v in data.model_dump(exclude={attr}).items():
        setattr(obj, k, v)
    setattr(obj, attr, [child(**x.model_dump()) for x in getattr(data, attr)])
    return save(db, obj)


def duplicate_content(db, model, content_id, user_id):
    old = readable(db, model, content_id, user_id)
    attr, _, _, _ = CONFIG[model]
    schema = {Workout: WorkoutCreate, Split: SplitCreate, TrainingPlan: TrainingPlanCreate}[model]
    data = schema.model_validate(old)
    obj = create_content(db, model, data, user_id, commit=False)
    obj.parent_id = old.id
    return save(db, obj)


def create_log(db, data, user_id):
    workout = readable(db, Workout, data.workout_id, user_id)
    prescriptions = {x.position: x for x in workout.exercises}
    results = []
    for result in data.results:
        item = prescriptions.get(result.position)
        if item is None or (item.sets is not None and result.set_number > item.sets):
            raise HTTPException(422, "Set result is outside the workout prescription")
        exercise = readable(db, Exercise, item.exercise_id, user_id, active=False)
        results.append(
            SetResult(
                **result.model_dump(),
                exercise_id=item.exercise_id,
                exercise_name=exercise.name,
                prescribed_sets=item.sets,
                prescribed_reps=item.reps,
                prescribed_weight_kg=item.weight_kg,
                prescribed_duration_seconds=item.duration_seconds,
                prescribed_distance_meters=item.distance_meters,
            )
        )
    obj = WorkoutLog(
        **data.model_dump(exclude={"results"}),
        user_id=user_id,
        workout_name=workout.name,
        results=results,
    )
    return save(db, obj)


def user_record(db, model, record_id, user_id):
    obj = db.scalar(select(model).where(model.id == record_id, model.user_id == user_id))
    if obj is None:
        raise HTTPException(404, "Record not found")
    return obj


def user_history(db, model, user_id, offset=0, limit=50):
    return list(
        db.scalars(
            select(model)
            .where(model.user_id == user_id)
            .order_by(model.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )


def record_weight(db, data, user_id):
    obj = db.scalar(
        select(WeightEntry).where(
            WeightEntry.user_id == user_id, WeightEntry.recorded_on == data.recorded_on
        )
    )
    if obj is None:
        obj = WeightEntry(user_id=user_id, **data.model_dump())
    else:
        obj.weight_kg = data.weight_kg
    return save(db, obj)


def progress_summary(db, user_id):
    logs = list(db.scalars(select(WorkoutLog).where(WorkoutLog.user_id == user_id)))
    weights = list(
        db.scalars(
            select(WeightEntry)
            .where(WeightEntry.user_id == user_id)
            .order_by(WeightEntry.recorded_on)
        )
    )
    return {
        "workouts_completed": sum(x.status == "completed" for x in logs),
        "workouts_partial": sum(x.status == "partial" for x in logs),
        "workouts_skipped": sum(x.status == "skipped" for x in logs),
        "total_duration_seconds": sum(x.duration_seconds or 0 for x in logs),
        "latest_weight_kg": weights[-1].weight_kg if weights else None,
        "weight_change_kg": round(weights[-1].weight_kg - weights[0].weight_kg, 2)
        if len(weights) > 1
        else None,
    }
