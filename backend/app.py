from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Workout, UserPreferences
from gpt_integration import GPTWorkoutGenerator
from workout_logic import WorkoutManager
import json

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

db.init_app(app)

# Initialize components
gpt_generator = GPTWorkoutGenerator()
workout_manager = WorkoutManager(gpt_generator)

@app.route('/')
def home():
    return jsonify({"message": "Workout Generator API"})

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.json

    user = User(
        username=data['username'],
        email=data['email'],
        fitness_goal=data.get('fitness_goal', 'general_fitness'),
        available_equipment=json.dumps(data.get('available_equipment', [])),
        time_constraint=data.get('time_constraint', 30),
        physical_limitations=json.dumps(data.get('physical_limitations', [])),
        experience_level=data.get('experience_level', 'beginner')
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user_id": user.id
    }), 201

@app.route('/api/users/<int:user_id>/workouts/generate', methods=['POST'])
def generate_workout(user_id):
    """Generate new workout for user"""
    user = User.query.get_or_404(user_id)

    workout_data = workout_manager.create_workout_plan(user, None)

    return jsonify({
        "message": "Workout generated successfully",
        "workout": workout_data
    })

@app.route('/api/users/<int:user_id>/workouts')
def get_user_workouts(user_id):
    """Get user's workout history"""
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.created_at.desc()).all()

    workout_list = []
    for workout in workouts:
        workout_list.append({
            "id": workout.id,
            "name": workout.name,
            "created_at": workout.created_at.isoformat(),
            "completed": workout.completed,
            "rating": workout.rating
        })

    return jsonify({"workouts": workout_list})

@app.route('/api/workouts/<int:workout_id>')
def get_workout_detail(workout_id):
    """Get detailed workout information"""
    workout = Workout.query.get_or_404(workout_id)

    return jsonify({
        "id": workout.id,
        "name": workout.name,
        "workout_data": json.loads(workout.workout_data),
        "created_at": workout.created_at.isoformat(),
        "rating": workout.rating,
        "feedback": workout.feedback
    })

@app.route('/api/workouts/<int:workout_id>/complete', methods=['POST'])
def complete_workout(workout_id):
    """Mark workout as completed with rating"""
    data = request.json

    workout_history = workout_manager.log_workout_completion(
        user_id=data['user_id'],
        workout_id=workout_id,
        performance_data=data.get('performance_data', {}),
        notes=data.get('notes'),
        rating=data.get('rating')
    )

    return jsonify({
        "message": "Workout completed successfully",
        "workout_history_id": workout_history.id
    })

@app.route('/api/users/<int:user_id>/analytics')
def get_user_analytics(user_id):
    """Get user workout analytics"""
    completed_workouts = Workout.query.filter_by(
        user_id=user_id,
        completed=True
    ).all()

    total_workouts = len(completed_workouts)
    average_rating = sum(w.rating for w in completed_workouts if w.rating) / len([w for w in completed_workouts if w.rating]) if completed_workouts else 0

    return jsonify({
        "total_completed_workouts": total_workouts,
        "average_rating": round(average_rating, 2),
        "completion_rate": f"{(total_workouts / max(1, len(Workout.query.filter_by(user_id=user_id).all())) * 100):.1f}%"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)