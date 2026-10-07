import os
import tempfile
from pathlib import Path

import pytest

# Tests NEVER use the application's configured production database.
_test_dir = tempfile.TemporaryDirectory(prefix="kenfit-tests-")
test_url = os.environ.get("KENFIT_TEST_DATABASE_URL")
if test_url:
    from sqlalchemy.engine import make_url

    parsed = make_url(test_url)
    if parsed.get_backend_name() != "postgresql" or parsed.database != "kenfit_test":
        raise RuntimeError(
            "PostgreSQL tests require a dedicated database named kenfit_test. Its tables are recreated."
        )
    os.environ["DATABASE_URL"] = test_url
else:
    os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_test_dir.name) / "tests.db")
os.environ["JWT_SECRET_KEY"] = "test-only-secret-at-least-thirty-two-characters"
os.environ["CORS_ORIGINS"] = "[]"

from alembic.config import Config
from fastapi.testclient import TestClient

from alembic import command
from app.app.main import app
from app.core.database import Base, SessionLocal, engine
from app.seed import seed


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        from sqlalchemy import text

        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    command.upgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "head")
    with SessionLocal() as db:
        seed(db)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def accounts(client):
    result = []
    for n in (1, 2):
        data = {"name": f"User {n}", "email": f"u{n}@example.com", "password": "TestPassword123!"}
        response = client.post("/auth/register", json=data)
        assert response.status_code == 201, response.text
        token = client.post(
            "/auth/login", json={"email": data["email"], "password": data["password"]}
        ).json()["access_token"]
        result.append({"Authorization": "Bearer " + token})
    return result
