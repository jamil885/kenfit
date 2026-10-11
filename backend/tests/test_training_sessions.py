def test_sessions_preserve_local_lifecycle_and_isolation(client, accounts):
    first, second = accounts
    workout = client.get("/workouts", headers=first).json()[0]
    response = client.post(
        "/training-sessions",
        headers=first,
        json={"workout_id": workout["id"], "notes": "Local API"},
    )
    assert response.status_code == 201, response.text
    session = response.json()
    assert session["status"] == "IN_PROGRESS"
    assert client.get(f"/training-sessions/{session['id']}", headers=second).status_code == 404
    assert (
        client.patch(
            f"/training-sessions/{session['id']}", headers=first, json={"notes": "Edited"}
        ).json()["notes"]
        == "Edited"
    )
    completed = client.post(f"/training-sessions/{session['id']}/complete", headers=first)
    assert completed.json()["status"] == "COMPLETED"
    assert completed.json()["finished_at"] is not None
    assert (
        client.post(f"/training-sessions/{session['id']}/cancel", headers=first).status_code == 409
    )
    cancelled = client.post("/training-sessions", headers=first, json={}).json()
    assert (
        client.post(f"/training-sessions/{cancelled['id']}/cancel", headers=first).json()["status"]
        == "CANCELLED"
    )
    private_response = client.post(f"/workouts/{workout['id']}/duplicate", headers=first)
    assert private_response.status_code == 201, private_response.text
    private = private_response.json()
    assert (
        client.post(
            "/training-sessions", headers=second, json={"workout_id": private["id"]}
        ).status_code
        == 404
    )
