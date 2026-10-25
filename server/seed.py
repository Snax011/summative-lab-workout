#!/usr/bin/env python3

from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db


with app.app_context():
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    exercises = [
        Exercise(name="Squat", category="Strength", equipment_needed=False),
        Exercise(name="Push-up", category="Strength", equipment_needed=False),
        Exercise(name="Treadmill Run", category="Cardio", equipment_needed=True),
    ]
    workouts = [
        Workout(date=date(2025, 1, 10), duration_minutes=45, notes="Leg and core"),
        Workout(date=date(2025, 1, 12), duration_minutes=30, notes="Upper body"),
    ]
    db.session.add_all(exercises + workouts)
    db.session.flush()

    db.session.add_all(
        [
            WorkoutExercise(
                workout=workouts[0], exercise=exercises[0], reps=10, sets=3
            ),
            WorkoutExercise(
                workout=workouts[0],
                exercise=exercises[2],
                duration_seconds=600,
            ),
            WorkoutExercise(
                workout=workouts[1], exercise=exercises[1], reps=12, sets=3
            ),
        ]
    )
    db.session.commit()
    print("Workout database seeded successfully.")
