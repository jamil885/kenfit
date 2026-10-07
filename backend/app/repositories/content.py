from sqlalchemy import or_, select


def visible(model, user_id):
    return or_(
        model.owner_id == user_id, (model.source == "SYSTEM") & (model.visibility == "platform")
    )


def list_content(db, model, user_id, offset=0, limit=50, search=None):
    stmt = select(model).where(visible(model, user_id), model.is_active.is_(True))
    if search:
        stmt = stmt.where(
            model.name.ilike(
                "%" + search.replace("%", "\\%").replace("_", "\\_") + "%", escape="\\"
            )
        )
    return list(db.scalars(stmt.order_by(model.id).offset(offset).limit(limit)))


def get_content(db, model, content_id, user_id, active=True):
    stmt = select(model).where(model.id == content_id, visible(model, user_id))
    if active:
        stmt = stmt.where(model.is_active.is_(True))
    return db.scalar(stmt)
