from datetime import date, timedelta
from email import policy
from email.parser import BytesParser

import pytest
from sqlalchemy import select, text

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.account import PasswordReset
from app.services.account import now


@pytest.fixture
def mailbox(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "mail_mode", "file")
    monkeypatch.setattr(settings, "mail_outbox", str(tmp_path))
    return tmp_path


def code(mailbox):
    file = sorted(mailbox.glob("*.eml"), key=lambda p: p.stat().st_mtime_ns)[-1]
    body = BytesParser(policy=policy.default).parsebytes(file.read_bytes()).get_content()
    return next(line for line in body.splitlines() if len(line.strip()) == 43)


def test_reset_single_use_expiry_and_revocation(client, accounts, mailbox):
    first, _ = accounts
    existing = client.post("/auth/forgot-password", json={"email": "u1@example.com"})
    token = code(mailbox)
    assert (
        client.post("/auth/forgot-password", json={"email": "absent@example.com"}).json()
        == existing.json()
    )
    assert len(list(mailbox.glob("*.eml"))) == 1
    with SessionLocal() as db:
        assert db.scalar(select(PasswordReset)).token_hash != token
    result = client.post(
        "/auth/reset-password", json={"token": token, "password": "NewPassword123!"}
    )
    assert result.status_code == 200, result.text
    assert client.get("/auth/me", headers=first).status_code == 401
    assert (
        client.post(
            "/auth/login", json={"email": "u1@example.com", "password": "TestPassword123!"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login", json={"email": "u1@example.com", "password": "NewPassword123!"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/auth/reset-password", json={"token": token, "password": "Different123!"}
        ).status_code
        == 400
    )
    client.post("/auth/forgot-password", json={"email": "u1@example.com"})
    token = code(mailbox)
    with SessionLocal() as db:
        row = db.scalar(select(PasswordReset))
        row.expires_at = now() - timedelta(seconds=1)
        db.commit()
    assert (
        client.post(
            "/auth/reset-password", json={"token": token, "password": "Different123!"}
        ).status_code
        == 400
    )


def test_recovery_limits(client, accounts, mailbox):
    for _ in range(4):
        assert (
            client.post("/auth/forgot-password", json={"email": "u1@example.com"}).status_code
            == 200
        )
    assert len(list(mailbox.glob("*.eml"))) == 3
    for _ in range(16):
        assert (
            client.post("/auth/forgot-password", json={"email": "none@example.com"}).status_code
            == 200
        )
    assert (
        client.post("/auth/forgot-password", json={"email": "none@example.com"}).status_code == 429
    )


def test_delete_account_isolation_and_password(client, accounts, mailbox):
    first, second = accounts
    workout = client.get("/workouts", headers=first).json()[0]
    private = client.post(f"/workouts/{workout['id']}/duplicate", headers=first).json()
    food = client.post(
        "/nutrition/foods",
        headers=first,
        json={"name": "Private meal", "calories": 100, "protein_g": 5, "carbs_g": 10, "fat_g": 4},
    ).json()
    assert "id" in food, food
    assert (
        client.post(
            "/nutrition/meals",
            headers=first,
            json={
                "food_id": food["id"],
                "recorded_on": str(date.today()),
                "meal": "lunch",
                "grams": 100,
            },
        ).status_code
        == 201
    )
    split = client.post(
        "/splits",
        headers=first,
        json={
            "name": "Private split",
            "cycle_days": 7,
            "days": [{"day": 1, "workout_id": private["id"]}],
        },
    ).json()
    assert "id" in split, split
    plan = client.post(
        "/training-plans",
        headers=first,
        json={
            "name": "Private plan",
            "weeks": 4,
            "goal": "strength",
            "split_id": split["id"],
            "schedule": [{"week": 1, "day": 1, "workout_id": private["id"]}],
        },
    ).json()
    assert "id" in plan, plan
    assert (
        client.post(
            "/workout-logs",
            headers=first,
            json={
                "workout_id": private["id"],
                "performed_on": str(date.today()),
                "status": "skipped",
                "results": [],
            },
        ).status_code
        == 201
    )
    client.post("/training-sessions", headers=first, json={"workout_id": private["id"]})
    client.post("/auth/forgot-password", json={"email": "u1@example.com"})
    assert (
        client.request(
            "DELETE", "/auth/me", headers=first, json={"password": "WrongPassword123!"}
        ).status_code
        == 400
    )
    assert client.get("/auth/me", headers=first).status_code == 200
    response = client.request(
        "DELETE", "/auth/me", headers=first, json={"password": "TestPassword123!"}
    )
    assert response.status_code == 204, response.text
    assert list(mailbox.glob("*.eml")) == []
    assert client.get("/auth/me", headers=first).status_code == 401
    assert client.get("/auth/me", headers=second).status_code == 200
    assert len(client.get("/workouts", headers=second).json()) > 0
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT count(*) FROM users WHERE id=1")) == 0
        assert conn.scalar(text("SELECT count(*) FROM workouts WHERE owner_id=1")) == 0
        assert conn.scalar(text("SELECT count(*) FROM password_resets WHERE user_id=1")) == 0


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="PostgreSQL archive")
def test_deletion_erases_pc_archive(client, accounts):
    first, second = accounts
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA kenfit_pc_account_test"))
        conn.execute(
            text("CREATE TABLE kenfit_pc_account_test.users (id integer PRIMARY KEY, email text)")
        )
        conn.execute(
            text(
                "INSERT INTO kenfit_pc_account_test.users VALUES (55,'u1@example.com'),(66,'u2@example.com')"
            )
        )
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE kenfit_pc_account_test.fitness_profiles (id integer PRIMARY KEY, user_id integer REFERENCES kenfit_pc_account_test.users(id))"
            )
        )
        conn.execute(
            text("INSERT INTO kenfit_pc_account_test.fitness_profiles VALUES (1,55),(2,66)")
        )
    try:
        response = client.request(
            "DELETE", "/auth/me", headers=first, json={"password": "TestPassword123!"}
        )
        assert response.status_code == 204, response.text
        with engine.connect() as conn:
            assert conn.scalar(text("SELECT count(*) FROM kenfit_pc_account_test.users")) == 1
            assert (
                conn.scalar(text("SELECT user_id FROM kenfit_pc_account_test.fitness_profiles"))
                == 66
            )
        assert client.get("/auth/me", headers=second).status_code == 200
    finally:
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA kenfit_pc_account_test CASCADE"))


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="PostgreSQL archive")
def test_incompatible_archive_rolls_back_account_deletion(client, accounts):
    first, _ = accounts
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA kenfit_pc_broken_test"))
        conn.execute(
            text("CREATE TABLE kenfit_pc_broken_test.users (id integer PRIMARY KEY, email text)")
        )
        conn.execute(text("INSERT INTO kenfit_pc_broken_test.users VALUES (55,'u1@example.com')"))
        conn.execute(
            text(
                "CREATE TABLE kenfit_pc_broken_test.unknown_reference (user_id integer REFERENCES kenfit_pc_broken_test.users(id))"
            )
        )
        conn.execute(text("INSERT INTO kenfit_pc_broken_test.unknown_reference VALUES (55)"))
    try:
        response = client.request(
            "DELETE", "/auth/me", headers=first, json={"password": "TestPassword123!"}
        )
        assert response.status_code == 409, response.text
        assert client.get("/auth/me", headers=first).status_code == 200
        with engine.connect() as conn:
            assert conn.scalar(text("SELECT count(*) FROM kenfit_pc_broken_test.users")) == 1
    finally:
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA kenfit_pc_broken_test CASCADE"))
