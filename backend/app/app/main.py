from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import app.models  # Register complete SQLAlchemy metadata.
from app.api.routes import (
    auth,
    exercise,
    fitness_profile,
    history,
    nutrition,
    recommendations,
    splits,
    training_plans,
    workouts,
)
from app.core.config import settings
from app.core.database import engine

app = FastAPI(
    title="KenFit API",
    description="Mobile fitness MVP: training, nutrition and progress",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
for module in (
    auth,
    fitness_profile,
    exercise,
    workouts,
    splits,
    training_plans,
    history,
    nutrition,
    recommendations,
):
    app.include_router(module.router)


@app.exception_handler(IntegrityError)
def integrity_error(request: Request, error: IntegrityError):
    return JSONResponse(
        status_code=409, content={"detail": "Operation conflicts with existing data"}
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "kenfit-api"}


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "database": "disconnected"}
        )
    return {"status": "ok", "database": "connected", "test": 1}
