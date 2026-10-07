from fastapi import HTTPException

from app.models.exercise import Exercise
from app.models.exercise_muscle import ExerciseMuscle
from app.models.muscle_group import MuscleGroup
from app.repositories.content import list_content
from app.services.content import archive, owned, readable, save


def validate_muscles(db, muscles):
    ids = [m.muscle_group_id for m in muscles]
    if len(ids) != len(set(ids)):
        raise HTTPException(422, "Duplicate muscle groups")
    if any(db.get(MuscleGroup, i) is None for i in ids):
        raise HTTPException(422, "Unknown muscle group")


def create_user_exercise(db, data, user_id):
    from app.services.discipline import ensure_discipline

    ensure_discipline(db, data.discipline)
    validate_muscles(db, data.muscle_groups)
    obj = Exercise(
        **data.model_dump(exclude={"muscle_groups"}),
        owner_id=user_id,
        source="USER",
        visibility="private",
    )
    obj.muscle_groups = [ExerciseMuscle(**m.model_dump()) for m in data.muscle_groups]
    return save(db, obj)


def get_exercise(db, exercise_id, user_id):
    return readable(db, Exercise, exercise_id, user_id)


def list_exercises(db, user_id, offset=0, limit=50, search=None):
    return list_content(db, Exercise, user_id, offset, limit, search)


def update_user_exercise(db, exercise_id, data, user_id):
    obj = owned(db, Exercise, exercise_id, user_id)
    if data.muscle_groups is not None:
        validate_muscles(db, data.muscle_groups)
    if data.discipline is not None:
        from app.services.discipline import ensure_discipline

        ensure_discipline(db, data.discipline)
    for k, v in data.model_dump(exclude_unset=True, exclude={"muscle_groups"}).items():
        setattr(obj, k, v)
    if data.muscle_groups is not None:
        obj.muscle_groups = [ExerciseMuscle(**m.model_dump()) for m in data.muscle_groups]
    return save(db, obj)


def delete_user_exercise(db, exercise_id, user_id):
    archive(db, Exercise, exercise_id, user_id)


def duplicate(db, exercise_id, user_id):
    old = readable(db, Exercise, exercise_id, user_id)
    fields = (
        "name",
        "description",
        "discipline",
        "modality",
        "exercise_type",
        "equipment",
        "difficulty",
        "instructions",
    )
    obj = Exercise(
        **{k: getattr(old, k) for k in fields},
        owner_id=user_id,
        source="USER",
        visibility="private",
        parent_id=old.id,
    )
    obj.muscle_groups = [
        ExerciseMuscle(muscle_group_id=m.muscle_group_id, role=m.role) for m in old.muscle_groups
    ]
    return save(db, obj)
