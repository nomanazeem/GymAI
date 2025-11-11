import json
from datetime import datetime, timedelta
from .models import db, Workout, WorkoutHistory

class WorkoutManager:
    def __init__(self, gpt_generator):
        self.gpt_generator = gpt_generator

    def create_workout_plan(self, user, user_preferences):
        """Create a new workout plan for user"""

        user_data = {
            'fitness_goal': user.fitness_goal,
            'available_equipment': json.loads(user.available_equipment),
            'time_constraint': user.time_constraint,
            'experience_level': user.experience_level,
            'physical_limitations': json.loads(user.physical_limitations) if user.physical_limitations else []
        }

        # Get recent workout history for context
        recent_workouts = Workout.query.filter_by(
            user_id=user.id
        ).order_by(Workout.created_at.desc()).limit(3).all()

        workout_history = None
        if recent_workouts:
            workout_history = self._format_workout_history(recent_workouts)

        # Generate workout using GPT
        workout_data = self.gpt_generator.generate_workout(user_data, workout_history)

        if workout_data:
            # Save workout to database
            workout = Workout(
                user_id=user.id,
                name=workout_data.get('workout_name', 'Custom Workout'),
                workout_data=json.dumps(workout_data),
                generated_by='gpt'
            )

            db.session.add(workout)
            db.session.commit()

            return workout_data
        else:
            return self._get_fallback_workout(user_data)

    def _format_workout_history(self, workouts):
        """Format workout history for GPT context"""
        history = []
        for workout in workouts:
            if workout.rating and workout.feedback:
                history.append(f"Rating: {workout.rating}/5, Feedback: {workout.feedback}")
        return "; ".join(history)

    def _get_fallback_workout(self, user_data):
        """Provide a fallback workout if GPT fails"""
        # Basic template-based workout
        return {
            "workout_name": "Backup Full Body Workout",
            "warmup": [
                {"exercise": "Jumping Jacks", "duration": "3 minutes", "description": "Moderate pace"},
                {"exercise": "Arm Circles", "duration": "1 minute", "description": "Forward and backward"},
                {"exercise": "Leg Swings", "duration": "1 minute", "description": "Front and side"}
            ],
            "main_workout": [
                {
                    "exercise": "Bodyweight Squats",
                    "muscle_group": "Legs",
                    "sets": 3,
                    "reps": "12-15",
                    "rest": "60s",
                    "instructions": "Keep chest up and knees behind toes",
                    "progressive_overload_note": "Add more reps or go deeper"
                }
            ],
            "cooldown": [
                {"exercise": "Quad Stretch", "duration": "30s each side", "description": "Hold gently"},
                {"exercise": "Hamstring Stretch", "duration": "30s each side", "description": "Keep back straight"}
            ],
            "total_estimated_duration": "30 minutes",
            "notes": "Consult with a fitness professional for personalized guidance"
        }

    def log_workout_completion(self, user_id, workout_id, performance_data, notes=None, rating=None):
        """Log completed workout and rating"""

        workout_history = WorkoutHistory(
            user_id=user_id,
            workout_id=workout_id,
            performance_data=json.dumps(performance_data),
            notes=notes
        )

        # Update workout completion status
        workout = Workout.query.get(workout_id)
        if workout:
            workout.completed = True
            workout.completion_date = datetime.utcnow()
            if rating:
                workout.rating = rating

        db.session.add(workout_history)
        db.session.commit()

        return workout_history