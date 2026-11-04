"""Create a small, repeatable set of sample data."""
from datetime import date, timedelta

from app import create_app, db
from app.models import Exercise, Workout, WorkoutExercise

app = create_app()

with app.app_context():
    db.create_all()
    db.session.query(WorkoutExercise).delete()
    db.session.query(Workout).delete()
    db.session.query(Exercise).delete()

    squat = Exercise(name="Barbell Squat", category="Strength", description="Compound lower-body movement.")
    plank = Exercise(name="Plank", category="Core", description="Maintain a straight body position.")
    pushup = Exercise(name="Push-up", category="Strength", description="Bodyweight upper-body movement.")
    session_a = Workout(name="Lower Body Strength", date=date.today(), notes="Controlled tempo.")
    session_b = Workout(name="Core and Conditioning", date=date.today() + timedelta(days=1))
    db.session.add_all([squat, plank, pushup, session_a, session_b])
    db.session.flush()
    db.session.add_all([
        WorkoutExercise(workout=session_a, exercise=squat, sets=4, reps=8),
        WorkoutExercise(workout=session_a, exercise=plank, sets=3, duration_seconds=45),
        WorkoutExercise(workout=session_b, exercise=plank, sets=3, duration_seconds=60),
        WorkoutExercise(workout=session_b, exercise=pushup, sets=3, reps=12),
    ])
    db.session.commit()
    print("Seeded 2 workouts, 3 exercises, and 4 workout-exercise assignments.")
