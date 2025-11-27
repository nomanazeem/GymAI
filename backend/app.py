from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Workout, UserPreferences
from gemini_integration import GeminiWorkoutGenerator
from workout_logic import WorkoutManager
import json
import hashlib

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

db.init_app(app)

# Initialize components with Gemini
gemini_generator = GeminiWorkoutGenerator()
workout_manager = WorkoutManager(gemini_generator)

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Workout Generator API with Gemini"})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register new user with password"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Check required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400

        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            return jsonify({"error": "Username already taken"}), 400

        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            fitness_goal=data.get('fitness_goal', 'general_fitness'),
            available_equipment=json.dumps(data.get('available_equipment', [])),
            time_constraint=data.get('time_constraint', 30),
            physical_limitations=json.dumps(data.get('physical_limitations', [])),
            experience_level=data.get('experience_level', 'beginner')
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """User login with email and password"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if user.password_hash != hash_password(data['password']):
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        })

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = User.query.get_or_404(user_id)

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "fitness_goal": user.fitness_goal,
            "available_equipment": json.loads(user.available_equipment) if user.available_equipment else [],
            "time_constraint": user.time_constraint,
            "physical_limitations": json.loads(user.physical_limitations) if user.physical_limitations else [],
            "experience_level": user.experience_level,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    })

@app.route('/api/users/<int:user_id>/workouts/generate', methods=['POST'])
def generate_workout(user_id):
    """Generate new workout for user using Gemini"""
    try:
        user = User.query.get_or_404(user_id)

        # Don't try to parse JSON if no data is sent
        # Just proceed without additional parameters
        workout_data = workout_manager.create_workout_plan(user, None)

        if workout_data:
            return jsonify({
                "message": "Workout generated successfully with Gemini",
                "workout": workout_data
            })
        else:
            return jsonify({
                "error": "Failed to generate workout with Gemini - No data returned"
            }), 500

    except Exception as e:
        print(f"Error in generate_workout endpoint: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": f"Error generating workout: {str(e)}"
        }), 500

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

    # Calculate average rating safely
    rated_workouts = [w for w in completed_workouts if w.rating is not None]
    average_rating = sum(w.rating for w in rated_workouts) / len(rated_workouts) if rated_workouts else 0

    # Calculate completion rate
    all_user_workouts = Workout.query.filter_by(user_id=user_id).all()
    total_user_workouts = len(all_user_workouts)
    completion_rate = (total_workouts / total_user_workouts * 100) if total_user_workouts > 0 else 0

    return jsonify({
        "total_completed_workouts": total_workouts,
        "average_rating": round(average_rating, 2),
        "completion_rate": f"{completion_rate:.1f}%",
        "total_workouts_generated": total_user_workouts
    })

@app.route('/api/test/gemini', methods=['GET'])
def test_gemini():
    """Test Gemini connection"""
    try:
        test_result = gemini_generator.test_connection()
        return jsonify({
            "status": "success" if "Hello" in test_result else "failed",
            "message": test_result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint to verify Gemini connection"""
    try:
        # Test Gemini connection
        test_result = gemini_generator.test_connection()
        return jsonify({
            "status": "healthy",
            "gemini_connection": "connected" if "Hello" in test_result else "issues",
            "message": "API is running with Gemini integration"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "gemini_connection": "failed",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)