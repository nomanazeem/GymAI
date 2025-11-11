import openai
import json
from config import Config

class GPTWorkoutGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    def generate_workout_prompt(self, user_data, workout_history=None):
        """Generate a comprehensive prompt for GPT"""

        base_prompt = f"""
        Create a personalized workout plan with the following constraints:

        FITNESS GOAL: {user_data['fitness_goal']}
        AVAILABLE EQUIPMENT: {', '.join(user_data['available_equipment'])}
        TIME CONSTRAINT: {user_data['time_constraint']} minutes
        EXPERIENCE LEVEL: {user_data['experience_level']}
        PHYSICAL LIMITATIONS: {', '.join(user_data['physical_limitations']) if user_data['physical_limitations'] else 'None'}

        Please structure the workout with:
        1. Warm-up (5-10 minutes)
        2. Main workout exercises with sets, reps, and rest periods
        3. Cool-down/stretching (5 minutes)

        Consider progressive overload and muscle group balance.
        """

        if workout_history:
            base_prompt += f"\n\nPrevious workout feedback: {workout_history}"

        base_prompt += """
        Return the response in this exact JSON format:
        {
            "workout_name": "Creative workout name",
            "warmup": [
                {"exercise": "name", "duration": "time", "description": "brief instructions"}
            ],
            "main_workout": [
                {
                    "exercise": "name",
                    "muscle_group": "target muscle",
                    "sets": number,
                    "reps": "rep range",
                    "rest": "rest time",
                    "instructions": "detailed instructions",
                    "progressive_overload_note": "how to progress next time"
                }
            ],
            "cooldown": [
                {"exercise": "name", "duration": "time", "description": "brief instructions"}
            ],
            "total_estimated_duration": "minutes",
            "notes": "general workout advice and precautions"
        }
        """

        return base_prompt

    def generate_workout(self, user_data, workout_history=None):
        """Generate workout using GPT"""

        prompt = self.generate_workout_prompt(user_data, workout_history)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert personal trainer and fitness coach. Create safe, effective, and personalized workout plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            workout_json = json.loads(response.choices[0].message.content)
            return workout_json

        except Exception as e:
            print(f"Error generating workout with GPT: {e}")
            return None