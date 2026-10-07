from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.training import GenerateRequest, ProgressionRequest, TrainingPlanResponse
from app.services.recommendations import generate, progression

router = APIRouter(prefix="/recommendations", tags=["Rule based recommendations"])


@router.post("/training-plan", response_model=TrainingPlanResponse, status_code=201)
def plan(
    data: GenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return generate(db, data, user.id)


@router.post("/progression")
def progress(
    data: ProgressionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return progression(db, data.log_id, user.id)
