from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.training import WeightEntry, WorkoutLog
from app.models.user import User
from app.schemas.training import WeightCreate, WeightResponse, WorkoutLogCreate, WorkoutLogResponse
from app.services.training import (
    create_log,
    progress_summary,
    record_weight,
    user_history,
    user_record,
)

router = APIRouter(tags=["History and progress"])


@router.post("/workout-logs", response_model=WorkoutLogResponse, status_code=201)
def log(
    data: WorkoutLogCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return create_log(db, data, user.id)


@router.get("/workout-logs", response_model=list[WorkoutLogResponse])
def logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return user_history(db, WorkoutLog, user.id, offset, limit)


@router.get("/workout-logs/{record_id}", response_model=WorkoutLogResponse)
def detail(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return user_record(db, WorkoutLog, record_id, user.id)


@router.delete("/workout-logs/{record_id}", status_code=204)
def delete_log(
    record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.delete(user_record(db, WorkoutLog, record_id, user.id))
    db.commit()


@router.put("/progress/weight", response_model=WeightResponse)
def weight(
    data: WeightCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return record_weight(db, data, user.id)


@router.get("/progress/weight", response_model=list[WeightResponse])
def weights(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return user_history(db, WeightEntry, user.id, offset, limit)


@router.delete("/progress/weight/{record_id}", status_code=204)
def delete_weight(
    record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.delete(user_record(db, WeightEntry, record_id, user.id))
    db.commit()


@router.get("/progress/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return progress_summary(db, user.id)
