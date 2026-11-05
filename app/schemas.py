"""Marshmallow request validation and response serialization schemas."""
from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class WorkoutInputSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    date = fields.Date(required=False, allow_none=False)
    notes = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))

    @validates_schema
    def normalize_and_validate(self, data, **kwargs):
        if "name" in data:
            data["name"] = data["name"].strip()
            if not data["name"]:
                raise ValidationError({"name": ["Name cannot be blank."]})
        if data.get("notes") is not None:
            data["notes"] = data["notes"].strip()


class ExerciseInputSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    category = fields.String(required=False, allow_none=True, validate=validate.Length(min=1, max=50))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))

    @validates_schema
    def normalize_and_validate(self, data, **kwargs):
        for key in ("name", "category", "description"):
            if isinstance(data.get(key), str):
                data[key] = data[key].strip()
        if "name" in data and not data["name"]:
            raise ValidationError({"name": ["Name cannot be blank."]})
        if data.get("category") == "":
            raise ValidationError({"category": ["Category cannot be blank when supplied."]})


class WorkoutExerciseInputSchema(Schema):
    exercise_id = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))
    sets = fields.Integer(required=False, allow_none=True, strict=True, validate=validate.Range(min=1))
    reps = fields.Integer(required=False, allow_none=True, strict=True, validate=validate.Range(min=1))
    duration_seconds = fields.Integer(required=False, allow_none=True, strict=True, validate=validate.Range(min=1))

    @validates_schema
    def require_measurement(self, data, **kwargs):
        if data.get("reps") is None and data.get("duration_seconds") is None:
            raise ValidationError("Provide reps, duration_seconds, or both.")


class ExerciseOutputSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    category = fields.String(allow_none=True, dump_only=True)
    description = fields.String(allow_none=True, dump_only=True)


class WorkoutExerciseOutputSchema(Schema):
    id = fields.Integer(dump_only=True)
    exercise = fields.Nested(ExerciseOutputSchema, dump_only=True)
    sets = fields.Integer(allow_none=True, dump_only=True)
    reps = fields.Integer(allow_none=True, dump_only=True)
    duration_seconds = fields.Integer(allow_none=True, dump_only=True)


class WorkoutOutputSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    date = fields.Date(dump_only=True)
    notes = fields.String(allow_none=True, dump_only=True)
    exercises = fields.Nested(
        WorkoutExerciseOutputSchema,
        many=True,
        attribute="workout_exercises",
        dump_only=True,
    )
