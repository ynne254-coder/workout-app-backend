# Workout Application Backend

A Flask REST API for personal trainers to manage workout sessions and reusable exercises. Each workout can contain multiple exercises; the `workout_exercises` association model stores sets, reps, and/or duration for each exercise in each workout.

## Requirements and installation

The assignment specifies Python 3.8.13 or newer. Install Python and Pipenv, then install the dependencies from the checked-in `Pipfile`:

```bash
python3 --version
python3 -m pip install --user pipenv
pipenv install --dev
```

If your system uses `pip` rather than `python3 -m pip`, use `pip install --user pipenv`. Run commands inside the Pipenv environment with `pipenv run` (or start a shell with `pipenv shell`).

## Database setup and seeding

The default database is SQLite at `instance/workouts.db`. Apply the included initial migration, then create sample data:

```bash
pipenv run flask --app app.py db upgrade
pipenv run python seed.py
```

The seed script creates two workouts, three reusable exercises, and four assignments. Re-running it resets the existing sample workout and exercise records before reseeding. The checked-in `migrations/` directory already contains the initial schema; do not run `flask db init` on a fresh clone.

## Run and test

```bash
pipenv run flask --app app.py run
pipenv run pytest
```

The health check is `GET /health`. The tests use an in-memory SQLite database and do not depend on seeded local data.

## API endpoints

All request bodies must be JSON objects. Invalid payloads return `400`, missing resources return `404`, and duplicate/relationship conflicts return `409`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | API status and resource overview |
| `GET` | `/health` | Health check |
| `GET` | `/workouts` | List workouts with assigned exercises |
| `POST` | `/workouts` | Create a workout (`name`, optional ISO `date`, optional `notes`) |
| `GET` | `/workouts/<id>` | Get a workout and its exercise assignments |
| `DELETE` | `/workouts/<id>` | Delete a workout and its assignments |
| `GET` | `/exercises` | List reusable exercises |
| `POST` | `/exercises` | Create an exercise (`name`, optional `category`, optional `description`) |
| `GET` | `/exercises/<id>` | Get one exercise |
| `DELETE` | `/exercises/<id>` | Delete an unassigned exercise; assigned exercises return `409` |
| `POST` | `/workouts/<id>/exercises` | Add an exercise using `exercise_id` and optional `sets`, plus `reps` and/or `duration_seconds` |

Example requests (with the server running on port 5000):

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

## Models, relationships, and validation

- `Workout` and `Exercise` are joined many-to-many by `WorkoutExercise`, which stores per-workout sets, reps, and duration.
- More than one database table constraint is present: bounded non-blank names/categories, positive workout metrics, and a required reps-or-duration measurement. Unique constraints prevent duplicate exercise names and duplicate assignments in one workout; foreign keys enforce valid relationships.
- SQLAlchemy model validators reject blank or overlong names/text and non-positive or non-integer sets/reps/duration.
- Marshmallow input schemas validate required values, types, text lengths, date format, positive IDs/counts, and assignment measurement rules.
- Marshmallow output schemas serialize exercises and workouts, including nested exercise-assignment records in workout responses.
