# Workout Tracker API

A Flask, SQLAlchemy, and Marshmallow backend for tracking workouts, reusable
exercises, and exercise-specific repetitions, sets, and duration.

## Setup

Install Pipenv, then install dependencies:

```bash
pipenv install
```

Apply the committed database migration and seed sample records:

```bash
cd server
export FLASK_APP=app.py
flask db upgrade head
python seed.py
```

To regenerate migrations after making model changes, first run
`flask db migrate -m "Describe schema change"` from `server/`.

The seed script clears and recreates its sample data, so it can be run safely
more than once.

## Run

From `server/`, start the API:

```bash
export FLASK_APP=app.py
flask run --port 5555
```

## Endpoints

All request and response bodies use JSON.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/workouts` | List workouts and their associated exercise details. |
| GET | `/workouts/<id>` | Get one workout; returns 404 when absent. |
| POST | `/workouts` | Create a workout. Requires `date` (`YYYY-MM-DD`) and positive `duration_minutes`; `notes` is optional. |
| DELETE | `/workouts/<id>` | Delete a workout and its exercise associations. |
| GET | `/exercises` | List reusable exercises. |
| GET | `/exercises/<id>` | Get one exercise; returns 404 when absent. |
| POST | `/exercises` | Create an exercise with `name`, `category`, and boolean `equipment_needed`. |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout associations. |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout. Requires one or more of `reps`, `sets`, and `duration_seconds`. |

Invalid request data returns a JSON `400`; missing resources return `404`;
duplicate exercises and duplicate workout/exercise pairs return `409`.

## Data integrity and validation

The schema uses unique exercise names, positive duration/reps/sets checks, and
non-empty exercise text checks. Model validators enforce positive integer
duration values and valid text/boolean values. Marshmallow schemas validate
request fields and produce structured nested JSON.

Run the test suite with:

```bash
pytest
```
