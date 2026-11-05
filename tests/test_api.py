import pytest

from app import create_app, db


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_create_workout_and_reject_blank_name(client):
    response = client.post("/workouts", json={"name": "  Leg Day  ", "date": "2026-11-04"})
    assert response.status_code == 201
    assert response.json["name"] == "Leg Day"
    assert response.json["exercises"] == []
    assert client.post("/workouts", json={"name": "   "}).status_code == 400


def test_create_and_reuse_exercise_across_workouts(client):
    exercise = client.post("/exercises", json={"name": "Plank", "category": "Core"})
    assert exercise.status_code == 201
    first = client.post("/workouts", json={"name": "Workout One"}).json
    second = client.post("/workouts", json={"name": "Workout Two"}).json
    assigned = client.post(f"/workouts/{first['id']}/exercises", json={"exercise_id": exercise.json["id"], "sets": 3, "duration_seconds": 30})
    assert assigned.status_code == 201
    assert client.post(f"/workouts/{second['id']}/exercises", json={"exercise_id": exercise.json["id"], "duration_seconds": 45}).status_code == 201
    detail = client.get(f"/workouts/{first['id']}").json
    assert len(detail["exercises"]) == 1
    assert detail["exercises"][0]["exercise"] == {
        "id": exercise.json["id"],
        "name": "Plank",
        "category": "Core",
        "description": None,
    }
    listed_workout = next(item for item in client.get("/workouts").json if item["id"] == first["id"])
    assert listed_workout["exercises"] == detail["exercises"]
    assert client.get(f"/exercises/{exercise.json['id']}").json["name"] == "Plank"


def test_assignment_validation_and_duplicate(client):
    exercise = client.post("/exercises", json={"name": "Squat"}).json
    workout = client.post("/workouts", json={"name": "Strength"}).json
    path = f"/workouts/{workout['id']}/exercises"
    assert client.post(path, json={"exercise_id": exercise["id"]}).status_code == 400
    assert client.post(path, json={"exercise_id": exercise["id"], "sets": 0, "reps": 5}).status_code == 400
    assert client.post(path, json={"exercise_id": exercise["id"], "sets": 3, "reps": 5}).status_code == 201
    assert client.post(path, json={"exercise_id": exercise["id"], "sets": 3, "reps": 5}).status_code == 409


def test_delete_and_missing_resources(client):
    workout = client.post("/workouts", json={"name": "Temporary"}).json
    assert client.delete(f"/workouts/{workout['id']}").status_code == 200
    assert client.get(f"/workouts/{workout['id']}").status_code == 404
    assert client.delete("/exercises/999").status_code == 404
