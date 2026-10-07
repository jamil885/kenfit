from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fitness_profile import FitnessProfile


def get_fitness_profile_by_user_id(
    db: Session,
    user_id: int,
) -> FitnessProfile | None:
    statement = select(FitnessProfile).where(FitnessProfile.user_id == user_id)

    return db.scalar(statement)


def create_fitness_profile(
    db: Session,
    user_id: int,
    birth_date,
    gender: str,
    height_cm: float,
    weight_kg: float,
    fitness_level: str,
    goal: str,
    **preferences,
) -> FitnessProfile:
    fitness_profile = FitnessProfile(
        user_id=user_id,
        birth_date=birth_date,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        fitness_level=fitness_level,
        goal=goal,
        **preferences,
    )

    db.add(fitness_profile)
    db.commit()
    db.refresh(fitness_profile)

    return fitness_profile


def update_fitness_profile(
    db: Session,
    fitness_profile: FitnessProfile,
    data: dict,
) -> FitnessProfile:
    for field, value in data.items():
        setattr(fitness_profile, field, value)

    db.commit()
    db.refresh(fitness_profile)

    return fitness_profile
