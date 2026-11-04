# Workout Application Backend

A REST API for personal trainers to manage workout sessions and reusable exercises. A workout can contain many exercises; the `workout_exercises` association model stores per-workout sets, reps, and/or duration.

## Stack

- Python 3.10+
- Flask 2.2.2, Flask-SQLAlchemy 3.0.3, Flask-Migrate 3.1.0
- Marshmallow 3.20.1
- SQLite by default (set `SQLALCHEMY_DATABASE_URI` in your environment/configuration to use another SQLAlchemy database)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pipenv
pipenv install --dev
```

If working inside the Pipenv environment, run commands with `pipenv run`. For a regular virtual environment instead, install the same dependencies from the Pipfile with `pip install Flask==2.2.2 Flask-Migrate==3.1.0 Flask-SQLAlchemy==3.0.3 Werkzeug==2.2.2 marshmallow==3.20.1 pytest`.

Initialize and apply database migrations:

```bash
export FLASK_APP=app.py
flask db init       # only the first time; this creates migrations/
flask db migrate -m "Create workout and exercise tables"
flask db upgrade
```

Seed example records (the script creates tables if needed and can be rerun; rerunning resets seeded workout/exercise records):

```bash
python seed.py
```

Run the development server:

```bash
flask run
```

The default database is SQLite at `instance/workouts.db`. The health check is `GET /health`.

## API endpoints

All request bodies are JSON. Validation failures return `400`; missing resources return `404`; uniqueness/relationship conflicts return `409`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | API status and resource overview |
| `GET` | `/health` | Health check |
| `GET` | `/workouts` | List workouts with their assigned exercises |
| `POST` | `/workouts` | Create a workout (`name`, optional ISO `date`, optional `notes`) |
| `GET` | `/workouts/<id>` | Get one workout and its exercise assignments |
| `DELETE` | `/workouts/<id>` | Delete a workout and its assignments |
| `GET` | `/exercises` | List reusable exercises |
| `POST` | `/exercises` | Create an exercise (`name`, optional `category`, optional `description`) |
| `GET` | `/exercises/<id>` | Get one exercise |
| `DELETE` | `/exercises/<id>` | Delete an unassigned exercise; assigned exercises return `409` |
| `POST` | `/workouts/<id>/exercises` | Assign an exercise using `exercise_id` and optional `sets`, plus `reps` and/or `duration_seconds` |

Example requests:

```bash
curl -X POST http://127.0.0.1:5000/workouts \
  -H 'Content-Type: application/json' \
  -d '{"name":"Full Body A","date":"2026-11-04","notes":"Week one"}'

curl -X POST http://127.0.0.1:5000/exercises \
  -H 'Content-Type: application/json' \
  -d '{"name":"Deadlift","category":"Strength"}'

curl -X POST http://127.0.0.1:5000/workouts/1/exercises \
  -H 'Content-Type: application/json' \
  -d '{"exercise_id":1,"sets":3,"reps":8}'
```

## Data integrity and validation

- Database checks enforce non-blank bounded workout/exercise names and categories, positive sets/reps/duration, and at least one of reps or duration for an assignment.
- Database constraints enforce unique exercise names and at most one assignment of a given exercise per workout; foreign keys protect relationships.
- SQLAlchemy model validators reject invalid names, text lengths, and non-positive/non-integer training values.
- Marshmallow schemas validate payload types, required values, text lengths, date parsing, positive IDs/counts, and assignment measurement requirements.

## Tests

```bash
pipenv run pytest
```
