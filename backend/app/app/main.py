
from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes.auth import router as auth_router
from app.core.database import engine
from app.api.routes.fitness_profile import router as fitness_profile_router
from app.api.routes.exercise import router as exercise_router
from app.api.routes.workout import router as workouts_router
from app.api.routes.splits import router as splits_router
from app.api.routes.training_plans import router as training_plans_router
from app.api.routes.training_sessions import router as training_sessions_router


app = FastAPI(
    title="KenFit API",
    description="Backend API for KenFit",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(fitness_profile_router)
app.include_router(exercise_router)
app.include_router(workouts_router)
app.include_router(splits_router)
app.include_router(training_plans_router)
app.include_router(training_sessions_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "kenfit-api",
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "status": "ok",
        "database": "connected",
        "test": value,
    }

