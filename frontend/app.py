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
    if 'current_workout' not in st.session_state:
        st.session_state.current_workout = None

def create_user():
    """Create new user form"""
    st.header("Create Your Profile")

    with st.form("user_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        fitness_goal = st.selectbox(
            "Fitness Goal",
            ["weight_loss", "muscle_gain", "endurance", "general_fitness", "sports_specific"]
        )
        experience_level = st.selectbox(
            "Experience Level",
            ["beginner", "intermediate", "advanced"]
        )
        time_constraint = st.slider("Time per session (minutes)", 15, 120, 45)

        available_equipment = st.multiselect(
            "Available Equipment",
            ["dumbbells", "barbell", "kettlebell", "resistance_bands", "pull_up_bar",
             "bench", "yoga_mat", "treadmill", "stationary_bike", "none"]
        )

        physical_limitations = st.text_area(
            "Physical Limitations (injuries, conditions, etc.)",
            placeholder="e.g., bad knee, lower back pain, asthma"
        )

        submitted = st.form_submit_button("Create Profile")

        if submitted:
            user_data = {
                "username": username,
                "email": email,
                "fitness_goal": fitness_goal,
                "experience_level": experience_level,
                "time_constraint": time_constraint,
                "available_equipment": available_equipment,
                "physical_limitations": [limitation.strip() for limitation in physical_limitations.split(',')] if physical_limitations else []
            }

            response = requests.post(f"{API_BASE_URL}/users", json=user_data)

            if response.status_code == 201:
                st.session_state.user_id = response.json()["user_id"]
                st.success("Profile created successfully!")
                st.rerun()
            else:
                st.error("Error creating profile")

def generate_workout():
    """Generate new workout"""
    st.header("Generate New Workout")

    if st.button("Generate Custom Workout"):
        with st.spinner("Creating your personalized workout..."):
            response = requests.post(f"{API_BASE_URL}/users/{st.session_state.user_id}/workouts/generate")

            if response.status_code == 200:
                workout_data = response.json()["workout"]
                st.session_state.current_workout = workout_data
                st.success("Workout generated successfully!")
                display_workout(workout_data)
            else:
                st.error("Error generating workout")

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

def user_analytics():
    """Display user analytics"""
    st.header("Your Fitness Analytics")

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

        # Placeholder for charts (you can add more detailed analytics here)
        st.info("More detailed analytics and progress tracking coming soon!")
    else:
        st.error("Error loading analytics")

def main():
    st.set_page_config(
        page_title="Personalized Workout Generator",
        page_icon="💪",
        layout="wide"
    )

    st.title("💪 Personalized Workout Generator")
    st.write("Get AI-powered workout plans tailored to your goals and equipment!")

    init_session_state()

    # Sidebar navigation
    if st.session_state.user_id:
        st.sidebar.success(f"User ID: {st.session_state.user_id}")

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
            st.info("Profile management coming soon!")

    else:
        create_user()

if __name__ == "__main__":
    main()