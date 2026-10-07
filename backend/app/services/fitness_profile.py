from datetime import date

from sqlalchemy.orm import Session

from app.repositories.fitness_profile import (
    create_fitness_profile,
    get_fitness_profile_by_user_id,
    update_fitness_profile,
)


def register_fitness_profile(
    db: Session,
    user_id: int,
    birth_date: date,
    gender: str,
    height_cm: float,
    weight_kg: float,
    fitness_level: str,
    goal: str,
    **preferences,
):
    existing_profile = get_fitness_profile_by_user_id(
        db,
        user_id,
    )

    if existing_profile:
        raise ValueError("Fitness profile already exists")

    return create_fitness_profile(
        db=db,
        user_id=user_id,
        birth_date=birth_date,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        fitness_level=fitness_level,
        goal=goal,
        **preferences,
    )


def get_user_fitness_profile(
    db: Session,
    user_id: int,
):
    return get_fitness_profile_by_user_id(
        db,
        user_id,
    )


def update_user_fitness_profile(
    db: Session,
    user_id: int,
    data: dict,
):
    profile = get_fitness_profile_by_user_id(
        db,
        user_id,
    )

    if profile is None:
        raise ValueError("Fitness profile not found")

    return update_fitness_profile(
        db=db,
        fitness_profile=profile,
        data=data,
    )
