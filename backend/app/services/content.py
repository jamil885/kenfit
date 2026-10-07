from fastapi import HTTPException

from app.repositories.content import get_content


def readable(db, model, content_id, user_id, active=True):
    obj = get_content(db, model, content_id, user_id, active)
    if obj is None:
        raise HTTPException(404, "Content not found")
    return obj


def owned(db, model, content_id, user_id):
    obj = readable(db, model, content_id, user_id)
    if obj.owner_id != user_id or obj.source != "USER":
        raise HTTPException(403, "Platform content is read only; duplicate it first")
    return obj


def save(db, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def archive(db, model, content_id, user_id):
    obj = owned(db, model, content_id, user_id)
    obj.is_active = False
    save(db, obj)
