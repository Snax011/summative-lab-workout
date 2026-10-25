from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workouts_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        viewonly=True,
        order_by="Exercise.id",
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError("Workout duration must be a positive integer.")
        return value

    @validates("date")
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError("Workout date must be a date.")
        return value

    def __repr__(self):
        return f"<Workout {self.id}, {self.date}, {self.duration_minutes} min>"


class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("name", name="uq_exercises_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_exercises_name_nonempty"),
        CheckConstraint(
            "length(trim(category)) > 0", name="ck_exercises_category_nonempty"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        viewonly=True,
        order_by="Workout.id",
    )

    @validates("name", "category")
    def validate_nonempty_text(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Exercise {key} is required.")
        return value.strip()

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be a boolean.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id}, {self.name}, {self.category}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint(
            "workout_id", "exercise_id", name="uq_workout_exercise_pair"
        ),
        CheckConstraint(
            "reps IS NULL OR reps > 0", name="ck_workout_exercises_reps_positive"
        ),
        CheckConstraint(
            "sets IS NULL OR sets > 0", name="ck_workout_exercises_sets_positive"
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_workout_exercises_duration_positive",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = db.Column(
        db.Integer, db.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps", "sets", "duration_seconds")
    def validate_positive_values(self, key, value):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value <= 0
        ):
            raise ValueError(f"{key} must be a positive integer when provided.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise {self.id}, workout={self.workout_id}, exercise={self.exercise_id}>"
