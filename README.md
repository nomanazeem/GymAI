

# Create virtual environment
python3 -m venv GymAI_env

# Activate virtual environment
# On macOS/Linux:
source GymAI/bin/activate
# On Windows:
# GymAI\Scripts\activate

# Install packages


# Setup and Installation
# 1. Backend Setup

cd backend
python -m GymAI_env GymAI_env
source GymAI_env/bin/activate  # On Windows: GymAI_env\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export FLASK_ENV=development

python app.py

# 2. Frontend Setup

cd frontend
pip install -r requirements.txt
streamlit run app.py

