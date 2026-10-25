from marshmallow import Schema, ValidationError, fields, post_load, validates_schema
from marshmallow.validate import Length, Range

from models import Exercise, Workout, WorkoutExercise


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=Range(min=1))
    sets = fields.Int(allow_none=True, validate=Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=Range(min=1))
    exercise = fields.Nested(lambda: ExerciseSchema(exclude=("workout_exercises",)))

    @post_load
    def make_workout_exercise(self, data, **kwargs):
        return WorkoutExercise(**data)


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    category = fields.Str(required=True, validate=Length(min=1, max=50))
    equipment_needed = fields.Bool(required=True)
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema,
        many=True,
        exclude=("exercise",),
        dump_only=True,
    )

    @validates_schema
    def validate_trimmed_strings(self, data, **kwargs):
        for field_name in ("name", "category"):
            if field_name in data and not data[field_name].strip():
                raise ValidationError({field_name: ["Must not be blank."]})

    @post_load
    def make_exercise(self, data, **kwargs):
        return Exercise(**data)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=Range(min=1))
    notes = fields.Str(load_default="", validate=Length(max=2000))
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema,
        many=True,
        exclude=("exercise",),
        dump_only=True,
    )

    @post_load
    def make_workout(self, data, **kwargs):
        return Workout(**data)


class WorkoutExerciseInputSchema(Schema):
    reps = fields.Int(allow_none=True, load_default=None, validate=Range(min=1))
    sets = fields.Int(allow_none=True, load_default=None, validate=Range(min=1))
    duration_seconds = fields.Int(
        allow_none=True, load_default=None, validate=Range(min=1)
    )

    @validates_schema
    def validate_activity_details(self, data, **kwargs):
        if all(data.get(key) is None for key in ("reps", "sets", "duration_seconds")):
            raise ValidationError("Provide reps, sets, or duration_seconds.")
