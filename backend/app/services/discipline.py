from app.models.discipline import Discipline


def ensure_discipline(db, code):
    if db.get(Discipline, code) is None:
        db.add(Discipline(code=code, name=code.replace("_", " ").title()))
        db.flush()
