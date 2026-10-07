from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.training import TrainingPlan
from app.models.user import User
from app.repositories.content import list_content
from app.schemas.training import TrainingPlanCreate, TrainingPlanResponse
from app.services.content import archive, readable
from app.services.training import create_content, duplicate_content, replace_content

router = APIRouter(prefix="/training-plans", tags=["training-plans"])


@router.get("", response_model=list[TrainingPlanResponse])
def listing(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_content(db, TrainingPlan, user.id, offset, limit, search)


@router.post("", response_model=TrainingPlanResponse, status_code=201)
def create(
    data: TrainingPlanCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return create_content(db, TrainingPlan, data, user.id)


@router.get("/{content_id}", response_model=TrainingPlanResponse)
def detail(content_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return readable(db, TrainingPlan, content_id, user.id)


@router.put("/{content_id}", response_model=TrainingPlanResponse)
def replace(
    content_id: int,
    data: TrainingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return replace_content(db, TrainingPlan, content_id, data, user.id)


@router.delete("/{content_id}", status_code=204)
def delete(content_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    archive(db, TrainingPlan, content_id, user.id)


@router.post("/{content_id}/duplicate", response_model=TrainingPlanResponse, status_code=201)
def duplicate(
    content_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return duplicate_content(db, TrainingPlan, content_id, user.id)
