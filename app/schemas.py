"""Request validation and response serialization."""
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
