from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # User preferences and constraints
    fitness_goal = db.Column(db.String(50))  # weight_loss, muscle_gain, endurance, etc.
    available_equipment = db.Column(db.Text)  # JSON string of equipment
    time_constraint = db.Column(db.Integer)  # minutes per session
    physical_limitations = db.Column(db.Text)  # JSON string of limitations
    experience_level = db.Column(db.String(20))  # beginner, intermediate, advanced

    # Relationships
    workouts = db.relationship('Workout', backref='user', lazy=True)
    preferences = db.relationship('UserPreferences', backref='user', uselist=False)

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preferred_days = db.Column(db.Text)  # JSON array of preferred days
    preferred_time = db.Column(db.String(20))
    workout_frequency = db.Column(db.Integer)  # sessions per week
    focus_areas = db.Column(db.Text)  # JSON array of muscle groups
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    workout_data = db.Column(db.Text)  # JSON string of complete workout
    generated_by = db.Column(db.String(20), default='gpt')  # gpt or template
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)

    # Ratings and feedback
    rating = db.Column(db.Integer)  # 1-5 stars
    feedback = db.Column(db.Text)
    difficulty_rating = db.Column(db.Integer)  # 1-10 scale

class WorkoutHistory(db.Model):
    __tablename__ = 'workout_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    performance_data = db.Column(db.Text)  # JSON string of actual performance
    notes = db.Column(db.Text)