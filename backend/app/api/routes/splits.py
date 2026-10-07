from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.training import Split
from app.models.user import User
from app.repositories.content import list_content
from app.schemas.training import SplitCreate, SplitResponse
from app.services.content import archive, readable
from app.services.training import create_content, duplicate_content, replace_content

router = APIRouter(prefix="/splits", tags=["splits"])


@router.get("", response_model=list[SplitResponse])
def listing(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_content(db, Split, user.id, offset, limit, search)


@router.post("", response_model=SplitResponse, status_code=201)
def create(
    data: SplitCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return create_content(db, Split, data, user.id)


@router.get("/{content_id}", response_model=SplitResponse)
def detail(content_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return readable(db, Split, content_id, user.id)


@router.put("/{content_id}", response_model=SplitResponse)
def replace(
    content_id: int,
    data: SplitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return replace_content(db, Split, content_id, data, user.id)


@router.delete("/{content_id}", status_code=204)
def delete(content_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    archive(db, Split, content_id, user.id)


@router.post("/{content_id}/duplicate", response_model=SplitResponse, status_code=201)
def duplicate(
    content_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return duplicate_content(db, Split, content_id, user.id)
