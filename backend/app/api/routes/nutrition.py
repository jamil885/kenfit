from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.nutrition import MealEntry
from app.models.user import User
from app.schemas.nutrition import (
    DaySummary,
    EstimateRequest,
    FoodCreate,
    FoodResponse,
    Macros,
    MealCreate,
    MealResponse,
    TargetCreate,
)
from app.services import nutrition as service
from app.services.training import user_record

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.get("/foods", response_model=list[FoodResponse])
def foods(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.list_foods(db, user.id, offset, limit, search)


@router.post("/foods", response_model=FoodResponse, status_code=201)
def create_food(
    data: FoodCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return service.create_food(db, data, user.id)


@router.get("/foods/{food_id}", response_model=FoodResponse)
def food(food_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.get_food(db, food_id, user.id)


@router.put("/foods/{food_id}", response_model=FoodResponse)
def update_food(
    food_id: int,
    data: FoodCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.update_food(db, food_id, data, user.id)


@router.get("/targets", response_model=Macros)
def targets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    obj = service.get_target(db, user.id)
    if obj is None:
        raise HTTPException(404, "Nutrition targets not set")
    return obj


@router.put("/targets", response_model=Macros)
def set_targets(
    data: TargetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return service.set_target(db, data, user.id)


@router.post("/estimate")
def estimate(
    data: EstimateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return service.estimate(db, data, user.id)


@router.post("/meals", response_model=MealResponse, status_code=201)
def create_meal(
    data: MealCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return service.create_meal(db, data, user.id)


@router.delete("/meals/{record_id}", status_code=204)
def delete_meal(
    record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.delete(user_record(db, MealEntry, record_id, user.id))
    db.commit()


@router.get("/summary", response_model=DaySummary)
def summary(
    recorded_on: date = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.day_summary(db, user.id, recorded_on)
