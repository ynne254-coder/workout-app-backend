"""REST API endpoints."""
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Exercise, Workout, WorkoutExercise
from app.schemas import (
    ExerciseInputSchema,
    ExerciseOutputSchema,
    WorkoutExerciseInputSchema,
    WorkoutExerciseOutputSchema,
    WorkoutInputSchema,
    WorkoutOutputSchema,
)

api = Blueprint("api", __name__)
workout_input = WorkoutInputSchema()
exercise_input = ExerciseInputSchema()
workout_exercise_input = WorkoutExerciseInputSchema()
workout_output = WorkoutOutputSchema()
workouts_output = WorkoutOutputSchema(many=True)
exercise_output = ExerciseOutputSchema()
exercises_output = ExerciseOutputSchema(many=True)
workout_exercise_output = WorkoutExerciseOutputSchema()


def parse_json(schema):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError({"_schema": ["Request body must be a JSON object."]})
    return schema.load(payload)


@api.get("/")
def index():
    return jsonify({"name": "Workout API", "status": "ok", "endpoints": ["/workouts", "/exercises"]})


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.get("/workouts")
def list_workouts():
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.id.desc()).all()
    return jsonify(workouts_output.dump(workouts))


@api.post("/workouts")
def create_workout():
    try:
        data = parse_json(workout_input)
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_output.dump(workout)), 201


@api.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found."}), 404
    return jsonify(workout_output.dump(workout))


@api.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found."}), 404
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted."}), 200


@api.get("/exercises")
def list_exercises():
    exercises = Exercise.query.order_by(Exercise.name.asc()).all()
    return jsonify(exercises_output.dump(exercises))


@api.post("/exercises")
def create_exercise():
    try:
        data = parse_json(exercise_input)
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400
    exercise = Exercise(**data)
    db.session.add(exercise)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "An exercise with that name already exists."}), 409
    return jsonify(exercise_output.dump(exercise)), 201


@api.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404
    return jsonify(exercise_output.dump(exercise))


@api.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404
    if exercise.workout_exercises:
        return jsonify({"error": "Cannot delete an exercise that is assigned to a workout."}), 409
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": "Exercise deleted."}), 200


@api.post("/workouts/<int:workout_id>/exercises")
def add_exercise_to_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found."}), 404
    try:
        data = parse_json(workout_exercise_input)
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400
    exercise = db.session.get(Exercise, data["exercise_id"])
    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404
    if any(link.exercise_id == exercise.id for link in workout.workout_exercises):
        return jsonify({"error": "This exercise is already assigned to the workout."}), 409
    link = WorkoutExercise(workout=workout, exercise=exercise, **{key: value for key, value in data.items() if key != "exercise_id"})
    db.session.add(link)
    db.session.commit()
    return jsonify(workout_exercise_output.dump(link)), 201
