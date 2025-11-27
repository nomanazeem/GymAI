import google.generativeai as genai
import json
from config import Config

class GeminiWorkoutGenerator:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)

        # Initialize the model with proper discovery
        self.model = self._initialize_supported_model()

        print(f"✅ Final model selected: {self.model.model_name}")

    def _initialize_supported_model(self):
        """Find and initialize a model that actually exists and supports generateContent"""
        try:
            print("🔍 Discovering available models...")
            available_models = list(genai.list_models())

            if not available_models:
                raise Exception("No models available from API")

            print(f"📋 Found {len(available_models)} total models")

            # Filter models that support generateContent
            supported_models = []
            for model in available_models:
                if 'generateContent' in model.supported_generation_methods:
                    supported_models.append(model)
                    print(f"✅ Supported: {model.name}")
                else:
                    print(f"❌ Not supported: {model.name} - Methods: {model.supported_generation_methods}")

            if not supported_models:
                raise Exception("No models support generateContent method")

            print(f"🎯 Found {len(supported_models)} models that support generateContent")

            # Try to use the most capable model first
            # gemini-1.5-flash-latest is usually available and good
            preferred_order = [
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-1.0-pro-latest',
                'gemini-1.0-pro',
                'gemini-pro'
            ]

            for preferred_name in preferred_order:
                for model in supported_models:
                    if model.name == preferred_name:
                        print(f"🚀 Using preferred model: {preferred_name}")
                        return genai.GenerativeModel(preferred_name)

            # If no preferred model found, use the first supported one
            first_supported = supported_models[0].name
            print(f"🔧 Using first supported model: {first_supported}")
            return genai.GenerativeModel(first_supported)

        except Exception as e:
            print(f"❌ Error in model discovery: {e}")
            # Last resort fallbacks
            fallback_models = [
                'models/gemini-pro',
                'gemini-pro',
                'models/gemini-1.0-pro',
                'gemini-1.0-pro'
            ]

            for fallback in fallback_models:
                try:
                    print(f"🔄 Trying fallback: {fallback}")
                    return genai.GenerativeModel(fallback)
                except Exception as e2:
                    print(f"❌ Fallback {fallback} failed: {e2}")
                    continue

            raise Exception("All model initialization attempts failed")

    def test_connection(self):
        """Test the Gemini API connection"""
        try:
            response = self.model.generate_content(
                "Reply with just the word 'Connected' and nothing else."
            )
            return f"✅ Connection test: {response.text}" if response else "❌ No response"
        except Exception as e:
            return f"❌ Connection failed: {e}"

    def generate_workout(self, user_data, workout_history=None):
        """Generate workout using Google Gemini"""
        try:
            prompt = self._create_workout_prompt(user_data, workout_history)
            print(f"🚀 Generating workout with model: {self.model.model_name}")

            response = self.model.generate_content(prompt)

            if not response.text:
                print("❌ Empty response from Gemini")
                return None

            print("✅ Received response from Gemini")

            # Clean and parse the response
            response_text = response.text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()

            print("📋 Response preview:", response_text[:200] + "..." if len(response_text) > 200 else response_text)

            # Parse JSON
            workout_json = json.loads(response_text)
            print("🎉 Successfully parsed workout JSON")
            return workout_json

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Raw response that failed to parse: {response.text}")
            return None

        except Exception as e:
            print(f"❌ Error generating workout: {e}")
            return None

    def _create_workout_prompt(self, user_data, workout_history=None):
        """Create a prompt for workout generation"""
        prompt = f"""
        Create a personalized workout plan as valid JSON.

        USER PROFILE:
        - Fitness Goal: {user_data['fitness_goal']}
        - Available Equipment: {', '.join(user_data['available_equipment'])}
        - Time Available: {user_data['time_constraint']} minutes
        - Experience Level: {user_data['experience_level']}
        - Physical Limitations: {', '.join(user_data['physical_limitations']) if user_data['physical_limitations'] else 'None'}

        REQUIREMENTS:
        - Include warm-up, main workout, and cool-down
        - Specify sets, reps, rest periods for each exercise
        - Consider the user's experience level and limitations
        - Total duration should be approximately {user_data['time_constraint']} minutes

        RESPONSE FORMAT (JSON only, no other text):
        {{
            "workout_name": "Creative workout name",
            "warmup": [
                {{"exercise": "name", "duration": "time", "description": "brief instructions"}}
            ],
            "main_workout": [
                {{
                    "exercise": "name",
                    "muscle_group": "target muscle",
                    "sets": number,
                    "reps": "rep range",
                    "rest": "rest time",
                    "instructions": "detailed instructions",
                    "progressive_overload_note": "how to progress next time"
                }}
            ],
            "cooldown": [
                {{"exercise": "name", "duration": "time", "description": "brief instructions"}}
            ],
            "total_estimated_duration": "minutes",
            "notes": "general workout advice and precautions"
        }}

        Return only the JSON object, no additional text.
        """

        return prompt