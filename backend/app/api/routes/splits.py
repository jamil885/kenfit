from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.split import (
    SplitCreate,
    SplitResponse,
    SplitUpdate,
)
from app.schemas.split_day import (
    SplitDayCreate,
    SplitDayResponse,
    SplitDayUpdate,
)
from app.services.split import (
    create_user_split,
    delete_user_split,
    get_user_splits,
    get_visible_split,
    update_user_split,
)
from app.services.split_day import (
    add_day_to_split,
    get_days_for_split,
    remove_day_from_split,
    update_day_in_split,
)


router = APIRouter(
    prefix="/splits",
    tags=["Splits"],
)


@router.post(
    "",
    response_model=SplitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_split(
    data: SplitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_user_split(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "",
    response_model=list[SplitResponse],
)
def get_splits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_splits(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{split_id}",
    response_model=SplitResponse,
)
def get_split(
    split_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    split = get_visible_split(
        db=db,
        user_id=current_user.id,
        split_id=split_id,
    )

    if split is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Split not found",
        )

    return split


@router.patch(
    "/{split_id}",
    response_model=SplitResponse,
)
def update_split(
    split_id: int,
    data: SplitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        split = update_user_split(
            db=db,
            user_id=current_user.id,
            split_id=split_id,
            data=data,
        )

        if split is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Split not found",
            )

        return split

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc




@router.post(
    "/{split_id}/days",
    response_model=SplitDayResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_split_day(
    split_id: int,
    data: SplitDayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return add_day_to_split(
            db=db,
            user_id=current_user.id,
            split_id=split_id,
            data=data,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{split_id}/days",
    response_model=list[SplitDayResponse],
)
def get_split_days(
    split_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_days_for_split(
            db=db,
            user_id=current_user.id,
            split_id=split_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{split_id}/days/{split_day_id}",
    response_model=SplitDayResponse,
)
def update_split_day(
    split_id: int,
    split_day_id: int,
    data: SplitDayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        split_day = update_day_in_split(
            db=db,
            user_id=current_user.id,
            split_id=split_id,
            split_day_id=split_day_id,
            data=data,
        )

        if split_day is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Split day not found",
            )

        return split_day

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{split_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_split(
    split_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_user_split(
            db=db,
            user_id=current_user.id,
            split_id=split_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Split not found",
            )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc