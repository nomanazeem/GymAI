import json
from datetime import datetime, timedelta
from models import db, Workout, WorkoutHistory

class WorkoutManager:
    def __init__(self, workout_generator):
        # Use consistent naming - both should be the same
        self.workout_generator = workout_generator  # This is the correct attribute name

    def create_workout_plan(self, user, user_preferences=None):
        """Create a new workout plan for user"""
        try:
            # Handle case where available_equipment or physical_limitations might be None
            available_equipment = json.loads(user.available_equipment) if user.available_equipment else []
            physical_limitations = json.loads(user.physical_limitations) if user.physical_limitations else []

            user_data = {
                'fitness_goal': user.fitness_goal,
                'available_equipment': available_equipment,
                'time_constraint': user.time_constraint,
                'experience_level': user.experience_level,
                'physical_limitations': physical_limitations
            }

            print(f"Generating workout for user {user.id} with data: {user_data}")

            # Get recent workout history for context
            recent_workouts = Workout.query.filter_by(
                user_id=user.id
            ).order_by(Workout.created_at.desc()).limit(3).all()

            workout_history = None
            if recent_workouts:
                workout_history = self._format_workout_history(recent_workouts)

            # Generate workout using the generator - use consistent attribute name
            workout_data = self.workout_generator.generate_workout(user_data, workout_history)

            if workout_data:
                # Save workout to database
                workout = Workout(
                    user_id=user.id,
                    name=workout_data.get('workout_name', 'Custom Workout'),
                    workout_data=json.dumps(workout_data),
                    generated_by='gemini'
                )

                db.session.add(workout)
                db.session.commit()

                return workout_data
            else:
                print("Generator returned no data, using fallback workout")
                return self._get_fallback_workout(user_data)

        except json.JSONDecodeError as e:
            print(f"JSON decode error in create_workout_plan: {e}")
            # Handle the case where equipment or limitations are not valid JSON
            user_data = {
                'fitness_goal': user.fitness_goal,
                'available_equipment': [],
                'time_constraint': user.time_constraint,
                'experience_level': user.experience_level,
                'physical_limitations': []
            }
            return self._get_fallback_workout(user_data)

        except Exception as e:
            print(f"Error in create_workout_plan: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _get_fallback_workout(self, user_data):
        """Provide a basic fallback workout when AI generation fails"""
        goal = user_data.get('fitness_goal', 'general_fitness')

        if goal == 'weight_loss':
            fallback_workout = {
                "workout_name": "Fat Burn Circuit",
                "warmup": [
                    {
                        "exercise": "Jumping Jacks",
                        "duration": "3 minutes",
                        "description": "Light cardio to get heart rate up"
                    },
                    {
                        "exercise": "High Knees",
                        "duration": "2 minutes",
                        "description": "Run in place bringing knees to chest"
                    }
                ],
                "main_workout": [
                    {
                        "exercise": "Bodyweight Squats",
                        "muscle_group": "Legs",
                        "sets": 3,
                        "reps": "15-20",
                        "rest": "30 seconds",
                        "instructions": "Stand with feet shoulder-width apart, lower down as if sitting in a chair",
                        "progressive_overload_note": "Increase reps or add jump squats"
                    },
                    {
                        "exercise": "Push-ups",
                        "muscle_group": "Chest",
                        "sets": 3,
                        "reps": "10-15",
                        "rest": "30 seconds",
                        "instructions": "Keep body straight, lower chest to floor",
                        "progressive_overload_note": "Increase reps or try decline push-ups"
                    },
                    {
                        "exercise": "Mountain Climbers",
                        "muscle_group": "Core",
                        "sets": 3,
                        "reps": "20-30",
                        "rest": "30 seconds",
                        "instructions": "In plank position, alternate bringing knees to chest",
                        "progressive_overload_note": "Increase speed or duration"
                    }
                ],
                "cooldown": [
                    {
                        "exercise": "Quad Stretch",
                        "duration": "30 seconds each side",
                        "description": "Standing quad stretch"
                    },
                    {
                        "exercise": "Hamstring Stretch",
                        "duration": "30 seconds each side",
                        "description": "Sit and reach for toes"
                    }
                ],
                "total_estimated_duration": "25 minutes",
                "notes": "Focus on keeping your heart rate up with minimal rest between exercises for maximum fat burning."
            }
        else:
            # General fitness fallback
            fallback_workout = {
                "workout_name": "Full Body Strength",
                "warmup": [
                    {
                        "exercise": "Arm Circles",
                        "duration": "1 minute",
                        "description": "Forward and backward arm circles"
                    },
                    {
                        "exercise": "Leg Swings",
                        "duration": "1 minute each side",
                        "description": "Forward and side leg swings"
                    }
                ],
                "main_workout": [
                    {
                        "exercise": "Bodyweight Squats",
                        "muscle_group": "Legs",
                        "sets": 3,
                        "reps": "12-15",
                        "rest": "45 seconds",
                        "instructions": "Stand with feet shoulder-width apart, lower down as if sitting in a chair",
                        "progressive_overload_note": "Increase reps or add jump squats"
                    },
                    {
                        "exercise": "Push-ups",
                        "muscle_group": "Chest",
                        "sets": 3,
                        "reps": "8-12",
                        "rest": "45 seconds",
                        "instructions": "Keep body straight, lower chest to floor",
                        "progressive_overload_note": "Increase reps or try decline push-ups"
                    }
                ],
                "cooldown": [
                    {
                        "exercise": "Quad Stretch",
                        "duration": "30 seconds each side",
                        "description": "Standing quad stretch"
                    },
                    {
                        "exercise": "Chest Stretch",
                        "duration": "30 seconds",
                        "description": "Stretch chest against doorway"
                    }
                ],
                "total_estimated_duration": "20 minutes",
                "notes": "This is a basic workout. For personalized plans, ensure AI generator is properly configured."
            }

        return fallback_workout

    def _format_workout_history(self, workouts):
        """Format workout history for context"""
        history = []
        for workout in workouts:
            try:
                workout_json = json.loads(workout.workout_data)
                history.append({
                    'name': workout_json.get('workout_name', 'Previous Workout'),
                    'exercises': workout_json.get('main_workout', [])[:3]  # First 3 exercises
                })
            except:
                continue
        return history

    def log_workout_completion(self, user_id, workout_id, performance_data=None, notes=None, rating=None):
        """Log workout completion - keep your existing implementation"""
        # Your existing implementation here
        pass