"""Database models and model-level validation for workouts and exercises."""
from datetime import date
import re

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

from app import db


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="ck_workout_name_length"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan",
        passive_deletes=True, order_by="WorkoutExercise.id",
    )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 100:
            raise ValueError("Workout name must contain 1 to 100 characters.")
        return value.strip()

    @validates("notes")
    def validate_notes(self, key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 500):
            raise ValueError("Workout notes must be 500 characters or fewer.")
        return value.strip() if isinstance(value, str) else value

    def to_dict(self, include_exercises=True):
        result = {"id": self.id, "name": self.name, "date": self.date.isoformat(), "notes": self.notes}
        if include_exercises:
            result["exercises"] = [item.to_dict() for item in self.workout_exercises]
        return result


class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="ck_exercise_name_length"),
        CheckConstraint("category IS NULL OR length(trim(category)) BETWEEN 1 AND 50", name="ck_exercise_category_length"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(500), nullable=True)

    workout_exercises = db.relationship("WorkoutExercise", back_populates="exercise", passive_deletes=True)

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 100:
            raise ValueError("Exercise name must contain 1 to 100 characters.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value is not None and (not isinstance(value, str) or not value.strip() or len(value.strip()) > 50):
            raise ValueError("Category must contain 1 to 50 characters when provided.")
        return value.strip() if isinstance(value, str) else value

    @validates("description")
    def validate_description(self, key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 500):
            raise ValueError("Exercise description must be 500 characters or fewer.")
        return value.strip() if isinstance(value, str) else value

    def to_dict(self):
        return {"id": self.id, "name": self.name, "category": self.category, "description": self.description}


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_workout_exercise_sets_positive"),
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_workout_exercise_reps_positive"),
        CheckConstraint("duration_seconds IS NULL OR duration_seconds > 0", name="ck_workout_exercise_duration_positive"),
        CheckConstraint("reps IS NOT NULL OR duration_seconds IS NOT NULL", name="ck_workout_exercise_has_measurement"),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("sets", "reps", "duration_seconds")
    def validate_positive_integer(self, key, value):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
            raise ValueError(f"{key.replace('_', ' ').title()} must be a positive integer.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "exercise": self.exercise.to_dict(),
            "sets": self.sets,
            "reps": self.reps,
            "duration_seconds": self.duration_seconds,
        }
