Personalized Workout Generator: Build a Flask-based API that creates tailored workout plans. Users input their fitness goals
, available equipment, time constraints, and any physical limitations through a Streamlit frontend. The system then leverages GPT to generate 
a customized workout plan , complete with exercises, sets, reps, and rest periods. The AI considers factors like progressive 
overload and muscle group balance in its recommendations. 
Users can save and rate their workouts, with this feedback used to refine future suggestions. 
All user profiles, preferences, and generated plans are stored in a database, allowing for detailed analytics and personalized fitness tracking over time.

# Create virtual environment
python3 -m venv GymAI_env

# Activate virtual environment
# On macOS/Linux:
source GymAI_env/bin/activate
# On Windows:
# GymAI\Scripts\activate

# Install packages


# Setup and Installation
# 1. Backend Setup

cd backend

pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export FLASK_ENV=development

python app.py

# 2. Frontend Setup

cd frontend
pip install -r requirements.txt
streamlit run app.py

