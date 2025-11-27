import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000/api"

def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'current_workout' not in st.session_state:
        st.session_state.current_workout = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

def safe_json_response(response):
    """Safely parse JSON response"""
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": f"Server returned non-JSON response: {response.status_code} - {response.text}"}

def login_user():
    """User login form"""
    st.header("🔐 Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return

            with st.spinner("Logging in..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={"email": email, "password": password}
                    )

                    if response.status_code == 200:
                        data = safe_json_response(response)
                        if "user_id" in data:
                            st.session_state.user_id = data["user_id"]
                            st.session_state.username = data["username"]
                            st.session_state.email = data["email"]
                            st.session_state.logged_in = True
                            st.success(f"Welcome back, {data['username']}!")
                            st.rerun()
                        else:
                            st.error(data.get("error", "Login failed"))
                    else:
                        data = safe_json_response(response)
                        error_msg = data.get("error", f"Login failed with status {response.status_code}")
                        st.error(error_msg)

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to server. Make sure the backend is running on http://localhost:5000")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

def register_user():
    """User registration form"""
    st.header("📝 Create New Account")

    with st.form("register_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input("Username*")
            email = st.text_input("Email*")
            password = st.text_input("Password*", type="password")

        with col2:
            fitness_goal = st.selectbox(
                "Fitness Goal*",
                ["weight_loss", "muscle_gain", "endurance", "general_fitness", "sports_specific"]
            )
            experience_level = st.selectbox(
                "Experience Level*",
                ["beginner", "intermediate", "advanced"]
            )
            confirm_password = st.text_input("Confirm Password*", type="password")

        time_constraint = st.slider("Time per session (minutes)*", 15, 120, 45)

        available_equipment = st.multiselect(
            "Available Equipment",
            ["dumbbells", "barbell", "kettlebell", "resistance_bands", "pull_up_bar",
             "bench", "yoga_mat", "treadmill", "stationary_bike", "none"]
        )

        physical_limitations = st.text_area(
            "Physical Limitations (injuries, conditions, etc.)",
            placeholder="e.g., bad knee, lower back pain, asthma"
        )

        submitted = st.form_submit_button("Create Account")

        if submitted:
            # Validation
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all required fields (*)")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return

            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "fitness_goal": fitness_goal,
                "experience_level": experience_level,
                "time_constraint": time_constraint,
                "available_equipment": available_equipment,
                "physical_limitations": [limitation.strip() for limitation in physical_limitations.split(',')] if physical_limitations else []
            }

            with st.spinner("Creating your account..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)

                    if response.status_code == 201:
                        data = safe_json_response(response)
                        st.session_state.user_id = data["user_id"]
                        st.session_state.username = data["username"]
                        st.session_state.email = email
                        st.session_state.logged_in = True
                        st.success("🎉 Account created successfully!")
                        st.rerun()
                    else:
                        data = safe_json_response(response)
                        error_msg = data.get("error", f"Registration failed with status {response.status_code}")
                        st.error(error_msg)

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to server. Make sure:")
                    st.write("1. The backend server is running")
                    st.write("2. It's running on http://localhost:5000")
                    st.write("3. Check the terminal for any backend errors")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

def logout_user():
    """Logout user"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.logged_in = False
    st.session_state.current_workout = None
    st.rerun()

def generate_workout():
    """Generate new workout"""
    st.header("Generate New Workout")

    if st.button("Generate Custom Workout"):
        with st.spinner("Creating your personalized workout..."):
            try:
                # Send empty JSON object instead of nothing
                response = requests.post(
                    f"{API_BASE_URL}/users/{st.session_state.user_id}/workouts/generate",
                    json={}  # Explicitly send empty JSON
                )

                if response.status_code == 200:
                    data = safe_json_response(response)
                    if "workout" in data:
                        workout_data = data["workout"]
                        st.session_state.current_workout = workout_data
                        st.success("Workout generated successfully!")
                        display_workout(workout_data)
                    else:
                        st.error("Workout data missing from response")
                        st.write("Response:", data)
                else:
                    data = safe_json_response(response)
                    error_msg = data.get("error", f"Error generating workout (Status: {response.status_code})")
                    st.error(error_msg)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to server. Make sure:")
                st.write("1. The backend server is running on http://localhost:5000")
                st.write("2. Check the backend terminal for errors")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.write("Please check the backend logs for more details")

def display_workout(workout_data):
    """Display workout details"""
    st.subheader(workout_data["workout_name"])

    # Warmup
    st.write("### 🔥 Warm-up")
    for exercise in workout_data["warmup"]:
        with st.expander(f"🧘 {exercise['exercise']} - {exercise['duration']}"):
            st.write(exercise["description"])

    # Main workout
    st.write("### 💪 Main Workout")
    for i, exercise in enumerate(workout_data["main_workout"], 1):
        with st.expander(f"{i}. {exercise['exercise']} - {exercise['muscle_group']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Sets:** {exercise['sets']}")
                st.write(f"**Reps:** {exercise['reps']}")
                st.write(f"**Rest:** {exercise['rest']}")
            with col2:
                st.write(f"**Instructions:** {exercise['instructions']}")
                st.write(f"**Progression:** {exercise['progressive_overload_note']}")

    # Cooldown
    st.write("### ❄️ Cool-down")
    for exercise in workout_data["cooldown"]:
        with st.expander(f"🔄 {exercise['exercise']} - {exercise['duration']}"):
            st.write(exercise["description"])

    # Notes
    st.info(f"**Notes:** {workout_data['notes']}")
    st.write(f"**Total Duration:** {workout_data['total_estimated_duration']}")

    # Rating and completion
    st.write("---")
    rate_workout()

def rate_workout():
    """Workout rating and feedback"""
    st.write("### Rate This Workout")

    rating = st.slider("How would you rate this workout?", 1, 5, 3)
    feedback = st.text_area("Additional feedback (optional)")

    if st.button("Complete Workout"):
        # In a real implementation, you'd save this to the database
        st.success("Workout completed and rated! Your feedback will help improve future workouts.")
        st.session_state.current_workout = None

def workout_history():
    """Display workout history"""
    st.header("Workout History")

    try:
        response = requests.get(f"{API_BASE_URL}/users/{st.session_state.user_id}/workouts")

        if response.status_code == 200:
            workouts = response.json()["workouts"]

            if not workouts:
                st.info("No workouts yet. Generate your first workout!")
                return

            for workout in workouts:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                with col1:
                    st.write(f"**{workout['name']}**")
                with col2:
                    st.write(workout['created_at'][:10])
                with col3:
                    st.write("✅" if workout['completed'] else "⏳")
                with col4:
                    if workout['rating']:
                        st.write(f"{'⭐' * workout['rating']}")

                st.write("---")
        else:
            st.error("Error loading workout history")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Make sure the backend is running.")

def user_analytics():
    """Display user analytics"""
    st.header("Your Fitness Analytics")

    try:
        response = requests.get(f"{API_BASE_URL}/users/{st.session_state.user_id}/analytics")

        if response.status_code == 200:
            analytics = response.json()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Completed Workouts", analytics["total_completed_workouts"])
            with col2:
                st.metric("Average Rating", analytics["average_rating"])
            with col3:
                st.metric("Completion Rate", analytics["completion_rate"])

            # Placeholder for charts
            st.info("More detailed analytics and progress tracking coming soon!")
        else:
            st.error("Error loading analytics")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Make sure the backend is running.")

def profile_settings():
    """User profile settings"""
    st.header("Profile Settings")

    try:
        response = requests.get(f"{API_BASE_URL}/users/{st.session_state.user_id}")

        if response.status_code == 200:
            user_data = response.json()["user"]

            st.write(f"**Username:** {user_data['username']}")
            st.write(f"**Email:** {user_data['email']}")
            st.write(f"**Fitness Goal:** {user_data['fitness_goal']}")
            st.write(f"**Experience Level:** {user_data['experience_level']}")
            st.write(f"**Time Constraint:** {user_data['time_constraint']} minutes")

            st.write("**Available Equipment:**")
            for equipment in user_data['available_equipment']:
                st.write(f"- {equipment}")

            if user_data['physical_limitations']:
                st.write("**Physical Limitations:**")
                for limitation in user_data['physical_limitations']:
                    st.write(f"- {limitation}")

            st.write("---")

            if st.button("Logout"):
                logout_user()
        else:
            st.error("Error loading profile data")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Make sure the backend is running.")

def main():
    st.set_page_config(
        page_title="Personalized Workout Generator",
        page_icon="💪",
        layout="wide"
    )

    st.title("💪 Personalized Workout Generator")
    st.write("Get AI-powered workout plans tailored to your goals and equipment!")

    init_session_state()

    # Show login/register or main app
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            login_user()

        with tab2:
            register_user()

    else:
        # Sidebar navigation for logged-in users
        st.sidebar.success(f"Welcome, {st.session_state.username}!")

        menu_options = [
            "Generate Workout",
            "Workout History",
            "Analytics",
            "Profile Settings"
        ]

        choice = st.sidebar.selectbox("Navigation", menu_options)

        if choice == "Generate Workout":
            generate_workout()
        elif choice == "Workout History":
            workout_history()
        elif choice == "Analytics":
            user_analytics()
        elif choice == "Profile Settings":
            profile_settings()

if __name__ == "__main__":
    main()