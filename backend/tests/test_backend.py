from datetime import date, timedelta

import jwt
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Exercise, User
from app.seed import seed

PROFILE = {
    "birth_date": "2000-01-01",
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "fitness_level": "beginner",
    "goal": "general_fitness",
}
EXERCISE = {
    "name": "Custom squat",
    "discipline": "strength",
    "exercise_type": "movement",
    "equipment": "bodyweight",
}


def create_exercise(client, h):
    response = client.post("/exercises", json=EXERCISE, headers=h)
    assert response.status_code == 201, response.text
    return response.json()


def create_workout(client, h, exercise_id):
    data = {
        "name": "My workout",
        "discipline": "strength",
        "exercises": [
            {"exercise_id": exercise_id, "position": 1, "sets": 2, "reps": 8, "weight_kg": 20}
        ],
    }
    response = client.post("/workouts", json=data, headers=h)
    assert response.status_code == 201, response.text
    return response.json(), data


def test_auth_and_duplicate_email(client, accounts):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers=accounts[0]).json()["email"] == "u1@example.com"
    assert (
        client.post(
            "/auth/register",
            json={"name": "Other", "email": "U1@example.com", "password": "TestPassword123!"},
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/auth/login", json={"email": "u1@example.com", "password": "WrongPassword"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login", json={"email": "U1@example.com", "password": "TestPassword123!"}
        ).status_code
        == 200
    )


@pytest.mark.parametrize(
    "payload", [{"sub": "1"}, {"sub": "nope", "exp": 4102444800}, {"sub": "1", "exp": 1}]
)
def test_invalid_tokens(client, payload):
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_disabled_account(client, accounts):
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.email == "u1@example.com"))
        u.is_active = False
        db.commit()
    assert client.get("/auth/me", headers=accounts[0]).status_code == 401
    assert (
        client.post(
            "/auth/login", json={"email": "u1@example.com", "password": "TestPassword123!"}
        ).status_code
        == 401
    )


def test_profiles_isolation_and_validation(client, accounts):
    h, other = accounts
    assert client.post("/fitness-profile", json=PROFILE, headers=h).status_code == 201
    assert client.post("/fitness-profile", json=PROFILE, headers=h).status_code == 409
    assert client.get("/fitness-profile", headers=other).status_code == 404
    assert (
        client.patch("/fitness-profile", json={"weight_kg": 80}, headers=h).json()["weight_kg"]
        == 80
    )
    assert client.patch("/fitness-profile", json={"weight_kg": None}, headers=h).status_code == 422
    assert (
        client.post(
            "/fitness-profile",
            json={**PROFILE, "birth_date": str(date.today() + timedelta(days=1))},
            headers=other,
        ).status_code
        == 422
    )


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_exercise_ownership(client, accounts, method):
    h, other = accounts
    e = create_exercise(client, h)
    kwargs = {"headers": other}
    if method == "patch":
        kwargs["json"] = {"name": "Stolen"}
    assert getattr(client, method)(f"/exercises/{e['id']}", **kwargs).status_code == 404
    assert all(x["id"] != e["id"] for x in client.get("/exercises", headers=other).json())


def test_system_content_and_duplicate(client, accounts):
    h = accounts[0]
    e = client.get("/exercises", headers=h).json()[0]
    assert (
        client.patch(f"/exercises/{e['id']}", json={"name": "Edited"}, headers=h).status_code == 403
    )
    copy = client.post(f"/exercises/{e['id']}/duplicate", headers=h)
    assert copy.status_code == 201, copy.text
    assert copy.json()["parent_id"] == e["id"]
    assert copy.json()["source"] == "USER"
    assert (
        client.patch(
            f"/exercises/{copy.json()['id']}", json={"name": "Edited"}, headers=h
        ).status_code
        == 200
    )


@pytest.mark.parametrize("resource", ["workouts", "splits", "training-plans"])
def test_official_templates(client, accounts, resource):
    h = accounts[0]
    obj = client.get("/" + resource, headers=h).json()[0]
    assert client.delete(f"/{resource}/{obj['id']}", headers=h).status_code == 403
    response = client.post(f"/{resource}/{obj['id']}/duplicate", headers=h)
    assert response.status_code == 201, response.text
    assert response.json()["parent_id"] == obj["id"]


def test_invalid_muscles_roll_back(client, accounts):
    h = accounts[0]
    before = len(client.get("/exercises", headers=h).json())
    assert (
        client.post(
            "/exercises",
            json={**EXERCISE, "muscle_groups": [{"muscle_group_id": 999, "role": "primary"}]},
            headers=h,
        ).status_code
        == 422
    )
    assert len(client.get("/exercises", headers=h).json()) == before
    assert create_exercise(client, h)["name"] == EXERCISE["name"]
    assert client.patch("/exercises/1", json={"name": None}, headers=h).status_code == 422


def test_workouts_and_private_references(client, accounts):
    h, other = accounts
    e = create_exercise(client, h)
    w, data = create_workout(client, h, e["id"])
    assert client.post("/workouts", json=data, headers=other).status_code == 404
    assert client.get(f"/workouts/{w['id']}", headers=other).status_code == 404
    assert (
        client.put(f"/workouts/{w['id']}", json={**data, "name": "New name"}, headers=h).status_code
        == 200
    )
    assert (
        client.post(
            "/workouts", json={**data, "exercises": data["exercises"] * 2}, headers=h
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/workouts",
            json={
                **data,
                "exercises": [
                    {
                        "exercise_id": e["id"],
                        "position": 1,
                        "duration_seconds": 60,
                        "distance_meters": 100,
                    }
                ],
            },
            headers=h,
        ).status_code
        == 201
    )


@pytest.mark.parametrize("resource", ["splits", "training-plans"])
def test_structure_and_links(client, accounts, resource):
    h, other = accounts
    e = create_exercise(client, h)
    w, _ = create_workout(client, h, e["id"])
    data = {
        "name": "My split",
        "cycle_days": 7,
        "days": [{"day": 1, "workout_id": w["id"]}, {"day": 2}],
    }
    if resource == "training-plans":
        data = {
            "name": "My plan",
            "weeks": 4,
            "goal": "strength",
            "schedule": [{"week": 1, "day": 1, "workout_id": w["id"]}],
        }
    response = client.post("/" + resource, json=data, headers=h)
    assert response.status_code == 201, response.text
    ident = response.json()["id"]
    assert client.post("/" + resource, json=data, headers=other).status_code == 404
    assert (
        client.put(f"/{resource}/{ident}", json={**data, "name": "Updated"}, headers=h).status_code
        == 200
    )
    copy = client.post(f"/{resource}/{ident}/duplicate", headers=h)
    assert copy.status_code == 201, copy.text
    assert client.delete(f"/{resource}/{ident}", headers=h).status_code == 204
    assert client.get(f"/{resource}/{ident}", headers=h).status_code == 404


def test_workout_log_snapshots_and_progression(client, accounts):
    h, other = accounts
    e = create_exercise(client, h)
    w, data = create_workout(client, h, e["id"])
    log = {
        "workout_id": w["id"],
        "performed_on": str(date.today()),
        "results": [
            {"position": 1, "set_number": i, "reps": 8, "weight_kg": 20, "rpe": 7} for i in (1, 2)
        ],
    }
    response = client.post("/workout-logs", json=log, headers=h)
    assert response.status_code == 201, response.text
    ident = response.json()["id"]
    assert response.json()["results"][0]["prescribed_reps"] == 8
    assert client.get(f"/workout-logs/{ident}", headers=other).status_code == 404
    suggestion = client.post("/recommendations/progression", json={"log_id": ident}, headers=h)
    assert suggestion.json()["suggestions"][0]["suggested_weight_kg"] == 20.5
    data["exercises"][0]["reps"] = 12
    assert client.put(f"/workouts/{w['id']}", json=data, headers=h).status_code == 200
    assert (
        client.get(f"/workout-logs/{ident}", headers=h).json()["results"][0]["prescribed_reps"] == 8
    )
    assert (
        client.post(
            "/workout-logs",
            json={**log, "results": [{**log["results"][0], "position": 99}]},
            headers=h,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/workout-logs", json={**log, "results": [], "status": "completed"}, headers=h
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/workout-logs", json={**log, "results": [], "status": "skipped"}, headers=h
        ).status_code
        == 201
    )
    assert client.delete(f"/exercises/{e['id']}", headers=h).status_code == 204
    assert client.get(f"/workout-logs/{ident}", headers=h).status_code == 200
    assert client.get("/progress/summary", headers=h).json()["workouts_completed"] == 1


def test_incomplete_sets_do_not_suggest_increase(client, accounts):
    h = accounts[0]
    e = create_exercise(client, h)
    w, _ = create_workout(client, h, e["id"])
    response = client.post(
        "/workout-logs",
        json={
            "workout_id": w["id"],
            "performed_on": str(date.today()),
            "results": [{"position": 1, "set_number": 1, "reps": 8, "weight_kg": 20, "rpe": 7}],
        },
        headers=h,
    )
    result = client.post(
        "/recommendations/progression", json={"log_id": response.json()["id"]}, headers=h
    ).json()
    assert result["suggestions"][0]["action"] == "repeat_and_review"


@pytest.mark.parametrize("discipline,days", [("strength", 3), ("running", 4), ("mobility", 2)])
def test_generator(client, accounts, discipline, days):
    h = accounts[0]
    client.post("/fitness-profile", json=PROFILE, headers=h)
    response = client.post(
        "/recommendations/training-plan",
        json={"discipline": discipline, "days_per_week": days, "weeks": 4},
        headers=h,
    )
    assert response.status_code == 201, response.text
    assert len(response.json()["schedule"]) == 4 * days
    assert response.json()["source"] == "USER"
    if discipline == "strength":
        assert (
            client.post(
                "/recommendations/training-plan", json={"days_per_week": 6}, headers=h
            ).status_code
            == 422
        )


def test_generator_needs_profile(client, accounts):
    assert (
        client.post("/recommendations/training-plan", json={}, headers=accounts[0]).status_code
        == 409
    )


def test_food_and_meal_snapshots(client, accounts):
    h, other = accounts
    data = {
        "name": "My food",
        "calories": 200,
        "protein_g": 10,
        "carbs_g": 30,
        "fat_g": 4,
        "serving_grams": 50,
    }
    food = client.post("/nutrition/foods", json=data, headers=h).json()
    assert client.get(f"/nutrition/foods/{food['id']}", headers=other).status_code == 404
    meal = {"food_id": food["id"], "recorded_on": str(date.today()), "meal": "lunch", "servings": 2}
    response = client.post("/nutrition/meals", json=meal, headers=h)
    assert response.status_code == 201, response.text
    assert response.json()["grams"] == 100
    assert response.json()["calories"] == 200
    assert (
        client.put(
            f"/nutrition/foods/{food['id']}", json={**data, "calories": 250}, headers=h
        ).status_code
        == 200
    )
    summary = client.get(
        "/nutrition/summary", params={"recorded_on": str(date.today())}, headers=h
    ).json()
    assert summary["consumed"]["calories"] == 200
    assert (
        client.delete(f"/nutrition/meals/{response.json()['id']}", headers=other).status_code == 404
    )
    assert (
        client.post("/nutrition/meals", json={**meal, "grams": 100}, headers=h).status_code == 422
    )
    assert client.post("/nutrition/meals", json=meal, headers=other).status_code == 404
    assert client.delete(f"/nutrition/meals/{response.json()['id']}", headers=h).status_code == 204
    assert (
        client.get(
            "/nutrition/summary", params={"recorded_on": str(date.today())}, headers=h
        ).json()["consumed"]["calories"]
        == 0
    )


def test_targets_and_estimation(client, accounts):
    h, other = accounts
    assert client.get("/nutrition/targets", headers=h).status_code == 404
    target = {"calories": 2000, "protein_g": 125, "carbs_g": 225, "fat_g": 66.7}
    assert client.put("/nutrition/targets", json=target, headers=h).status_code == 200
    assert client.get("/nutrition/targets", headers=other).status_code == 404
    assert (
        client.put(
            "/nutrition/targets",
            json={**target, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            headers=h,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/nutrition/estimate", json={"equation_sex": "male", "activity_factor": 1.2}, headers=h
        ).status_code
        == 409
    )
    client.post("/fitness-profile", json=PROFILE, headers=h)
    response = client.post(
        "/nutrition/estimate", json={"equation_sex": "male", "activity_factor": 1.2}, headers=h
    )
    assert response.status_code == 200, response.text
    values = {k: response.json()[k] for k in target}
    assert client.put("/nutrition/targets", json=values, headers=h).status_code == 200


def test_weight_upsert_and_progress(client, accounts):
    h = accounts[0]
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    assert (
        client.put(
            "/progress/weight", json={"recorded_on": yesterday, "weight_kg": 80}, headers=h
        ).status_code
        == 200
    )
    client.put("/progress/weight", json={"recorded_on": today, "weight_kg": 79}, headers=h)
    client.put("/progress/weight", json={"recorded_on": today, "weight_kg": 78}, headers=h)
    assert len(client.get("/progress/weight", headers=h).json()) == 2
    assert client.get("/progress/summary", headers=h).json()["weight_change_kg"] == -2
    assert (
        client.put(
            "/progress/weight",
            json={"recorded_on": str(date.today() + timedelta(days=1)), "weight_kg": 78},
            headers=h,
        ).status_code
        == 422
    )


def test_seed_idempotency(client):
    with SessionLocal() as db:
        before = len(list(db.scalars(select(Exercise))))
        seed(db)
        seed(db)
        assert len(list(db.scalars(select(Exercise)))) == before


def test_openapi_and_pagination(client, accounts):
    assert client.get("/openapi.json").status_code == 200
    assert len(client.get("/exercises?limit=2", headers=accounts[0]).json()) == 2
    assert client.get("/exercises?limit=1000", headers=accounts[0]).status_code == 422
    assert client.get("/health/database").json()["test"] == 1


def test_onboarding_preferences_drive_generator(client, accounts):
    h = accounts[0]
    response = client.post(
        "/fitness-profile",
        json={
            **PROFILE,
            "days_per_week": 2,
            "session_minutes": 10,
            "preferred_discipline": "running",
        },
        headers=h,
    )
    assert response.status_code == 201, response.text
    plan = client.post("/recommendations/training-plan", json={}, headers=h)
    assert plan.status_code == 201, plan.text
    assert len(plan.json()["schedule"]) == 8
    workout = client.get(f"/workouts/{plan.json()['schedule'][0]['workout_id']}", headers=h).json()
    assert workout["exercises"][0]["duration_seconds"] == 600
    assert (
        client.patch(
            "/fitness-profile", json={"preferred_discipline": "cycling"}, headers=h
        ).status_code
        == 200
    )
    assert client.post("/recommendations/training-plan", json={}, headers=h).status_code == 422


def test_mass_assignment_is_rejected(client, accounts):
    h = accounts[0]
    assert (
        client.post(
            "/exercises", json={**EXERCISE, "source": "SYSTEM", "owner_id": 2}, headers=h
        ).status_code
        == 422
    )
    assert client.patch("/fitness-profile", json={"user_id": 2}, headers=h).status_code == 422


def test_custom_discipline_catalog(client, accounts):
    h = accounts[0]
    response = client.post("/exercises", json={**EXERCISE, "discipline": "sport_custom"}, headers=h)
    assert response.status_code == 201, response.text
    assert any(
        x["code"] == "sport_custom" for x in client.get("/exercises/disciplines", headers=h).json()
    )


def test_estimate_equation_and_requires_explicit_save(client, accounts):
    h = accounts[0]
    client.post("/fitness-profile", json=PROFILE, headers=h)
    today = date.today()
    age = today.year - 2000 - ((today.month, today.day) < (1, 1))
    for sex, constant in (("male", 5), ("female", -161)):
        estimate = client.post(
            "/nutrition/estimate", json={"equation_sex": sex, "activity_factor": 1.2}, headers=h
        )
        assert estimate.status_code == 200, estimate.text
        assert estimate.json()["calories"] == round(
            (10 * 75 + 6.25 * 175 - 5 * age + constant) * 1.2
        )
    assert client.get("/nutrition/targets", headers=h).status_code == 404


def test_failed_update_keeps_old_prescription(client, accounts):
    h, other = accounts
    e = create_exercise(client, h)
    w, data = create_workout(client, h, e["id"])
    foreign = create_exercise(client, other)
    data["exercises"][0]["exercise_id"] = foreign["id"]
    assert client.put(f"/workouts/{w['id']}", json=data, headers=h).status_code == 404
    assert (
        client.get(f"/workouts/{w['id']}", headers=h).json()["exercises"][0]["exercise_id"]
        == e["id"]
    )
