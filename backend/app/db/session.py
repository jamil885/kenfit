from app.core.database import SessionLocal


def get_db():
    with SessionLocal() as db:
        try:
            yield db
        except Exception:
            db.rollback()
            raise
