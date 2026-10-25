from datetime import date

import pytest

from app import app
from models import Exercise, Workout, WorkoutExercise, db


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "test.db"
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
    )
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_create_workout_and_add_exercise(client):
    workout_response = client.post(
        "/workouts",
        json={"date": "2025-02-01", "duration_minutes": 40, "notes": "Morning"},
    )
    exercise_response = client.post(
        "/exercises",
        json={
            "name": "Deadlift",
            "category": "Strength",
            "equipment_needed": True,
        },
    )
    assert workout_response.status_code == 201
    assert exercise_response.status_code == 201

    association_response = client.post(
        f"/workouts/{workout_response.json['id']}/exercises/"
        f"{exercise_response.json['id']}/workout_exercises",
        json={"reps": 5, "sets": 3},
    )
    assert association_response.status_code == 201
    assert association_response.json["exercise"]["name"] == "Deadlift"
    assert client.get(f"/workouts/{workout_response.json['id']}").json[
        "workout_exercises"
    ][0]["sets"] == 3
    assert client.get("/workouts").status_code == 200
    assert client.get("/exercises").status_code == 200
    assert client.get(f"/exercises/{exercise_response.json['id']}").json["name"] == "Deadlift"

    duplicate_response = client.post(
        f"/workouts/{workout_response.json['id']}/exercises/"
        f"{exercise_response.json['id']}/workout_exercises",
        json={"reps": 5, "sets": 3},
    )
    assert duplicate_response.status_code == 409

    assert client.delete(f"/exercises/{exercise_response.json['id']}").status_code == 204
    assert client.get(f"/exercises/{exercise_response.json['id']}").status_code == 404


def test_rejects_invalid_schema_data(client):
    response = client.post(
        "/workouts",
        json={"date": "not-a-date", "duration_minutes": 0},
    )
    assert response.status_code == 400

    response = client.post(
        "/exercises",
        json={"name": "  ", "category": "Strength", "equipment_needed": False},
    )
    assert response.status_code == 400


def test_missing_resources_and_cascades(client):
    assert client.get("/workouts/100").status_code == 404
    assert client.delete("/exercises/100").status_code == 404

    with app.app_context():
        workout = Workout(date=date(2025, 1, 1), duration_minutes=20)
        exercise = Exercise(
            name="Plank",
            category="Core",
            equipment_needed=False,
        )
        db.session.add_all([workout, exercise])
        db.session.flush()
        link = WorkoutExercise(
            workout=workout,
            exercise=exercise,
            duration_seconds=30,
        )
        db.session.add(link)
        db.session.commit()
        workout_id = workout.id

    assert client.delete(f"/workouts/{workout_id}").status_code == 204
    with app.app_context():
        assert WorkoutExercise.query.count() == 0


def test_model_validations_and_workout_delete(client):
    with app.app_context():
        with pytest.raises(ValueError):
            Workout(date=date(2025, 1, 1), duration_minutes=0)
        with pytest.raises(ValueError):
            Exercise(name=" ", category="Strength", equipment_needed=False)
        with pytest.raises(ValueError):
            WorkoutExercise(reps=0)

    created = client.post(
        "/workouts",
        json={"date": "2025-02-02", "duration_minutes": 25},
    )
    assert created.status_code == 201
    assert client.delete(f"/workouts/{created.json['id']}").status_code == 204
    assert client.get(f"/workouts/{created.json['id']}").status_code == 404


def test_association_schema_requires_training_details(client):
    workout = client.post(
        "/workouts",
        json={"date": "2025-02-03", "duration_minutes": 25},
    ).json
    exercise = client.post(
        "/exercises",
        json={
            "name": "Lunge",
            "category": "Strength",
            "equipment_needed": False,
        },
    ).json

    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={},
    )
    assert response.status_code == 400
