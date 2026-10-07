from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.muscle_group import MuscleGroup
from app.models.user import User
from app.schemas.common import Schema
from app.schemas.exercise import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from app.services import exercise as service

router = APIRouter(prefix="/exercises", tags=["Exercises"])


class DisciplineResponse(Schema):
    code: str
    name: str


@router.get("/disciplines", response_model=list[DisciplineResponse])
def disciplines(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.models.discipline import Discipline

    return list(db.scalars(select(Discipline).order_by(Discipline.code)))


class MuscleResponse(Schema):
    id: int
    name: str
    description: str | None


@router.get("/muscle-groups", response_model=list[MuscleResponse])
def muscle_groups(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(MuscleGroup).order_by(MuscleGroup.id)))


@router.post("", response_model=ExerciseResponse, status_code=201)
def create(
    data: ExerciseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return service.create_user_exercise(db, data, user.id)


@router.get("", response_model=list[ExerciseResponse])
def listing(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.list_exercises(db, user.id, offset, limit, search)


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def detail(exercise_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.get_exercise(db, exercise_id, user.id)


@router.patch("/{exercise_id}", response_model=ExerciseResponse)
def update(
    exercise_id: int,
    data: ExerciseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.update_user_exercise(db, exercise_id, data, user.id)


@router.delete("/{exercise_id}", status_code=204)
def delete(exercise_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.delete_user_exercise(db, exercise_id, user.id)


@router.post("/{exercise_id}/duplicate", response_model=ExerciseResponse, status_code=201)
def duplicate(
    exercise_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return service.duplicate(db, exercise_id, user.id)
