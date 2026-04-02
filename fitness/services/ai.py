import os
import base64
import json
from groq import Groq
from ..models import Profile, Activity, NutritionLog, DailyStats
import subprocess

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    # -------------------- IMAGE --------------------
    def analyze_meal_image(self, image_path):
        if not self.client:
            return self._mock_meal_analysis()

        try:
            # encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Identify the food in this image and estimate calories, protein, carbs, and fats. "
                                    "Return ONLY JSON in this format: "
                                    "{\"food_name\": \"...\", \"calories\": 0, \"protein\": 0, \"carbs\": 0, \"fats\": 0, \"health_score\": 0}"
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.3,
            )

            content = response.choices[0].message.content

            # ✅ Try parsing JSON directly
            try:
                return json.loads(content)

            except:
                # ✅ Extract JSON if model added extra text
                import re

                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    return json.loads(match.group())

                return self._mock_meal_analysis()

        except Exception as e:
            print(f"Groq Vision Error: {e}")
            return self._mock_meal_analysis()

    # -------------------- CHAT --------------------
    def get_coach_insight(self, user_stats, recent_activities):
        if not self.client:
            return "Keep up the great work! You're moving in the right direction."

        prompt = f"""
        User Stats: {user_stats}
        Recent Activities: {recent_activities}

        Act as an elite AI Fitness Coach. Give a short (1-2 lines), motivating and helpful response.
        """

        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional fitness coach who gives concise and motivating advice.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Groq Coach Error: {e}")
            return "Your evolution is progressing nicely. Consistency is key!"

    # -------------------- VOICE --------------------
    def transcribe_voice_meal(self, audio_path):
        if not self.client:
            return "AI not configured"

        try:
            wav_path = audio_path + ".wav"

            # 🔥 Convert to WAV (IMPORTANT)
            subprocess.run([
                "ffmpeg",
                "-i", audio_path,
                "-ar", "16000",
                "-ac", "1",
                wav_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            with open(wav_path, "rb") as file:
                response = self.client.audio.transcriptions.create(
                    file=(wav_path, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    temperature=0.0
                )

            os.remove(wav_path)

            print("✅ Transcription:", response.text)

            return response.text

        except Exception as e:
            print("🔥 Transcription error:", e)
            return "Could not understand audio"
  
    # -------------------- MOCK --------------------
    def _mock_meal_analysis(self):
        return {
            "food_name": "Detected Meal (Mock)",
            "calories": 450,
            "protein": 25,
            "carbs": 40,
            "fats": 15,
            "health_score": 85,
        }