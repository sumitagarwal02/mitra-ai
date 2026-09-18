import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your .env file!")

# 2. Initialize Gemini Client
client = genai.Client(api_key=api_key)

# 3. Define structured output schema
class MitraRecommendation(BaseModel):
    mood_analysis: str = Field(description="Empathetic assessment of the user's current vibe and energy level.")
    youtube_search_query: str = Field(description="Search query to find a matching YouTube video (e.g., '5 min breathwork for anxiety').")
    micro_exercise: str = Field(description="A quick 2-minute actionable physical or mental reset exercise.")
    journal_prompt: str = Field(description="A targeted prompt for diary or journal writing.")

def analyze_vibe_and_recommend(user_checkin_responses: str) -> MitraRecommendation:
    """Analyzes user responses and returns structured recommendations using an active account model."""
    system_prompt = """
    You are Mitra, a warm, authentic, and grounded digital friend. 
    Analyze the user's check-in responses to understand their current mood and energy level.
    Keep your tone supportive and conversational—like a good peer, not a rigid lecturer or therapist.
    """

    user_prompt = f"User Check-in Answers:\n{user_checkin_responses}"

    # Fetch available models directly from your Gemini account
    discovered_models = []
    try:
        for m in client.models.list():
            clean_name = m.name.split("/")[-1]
            if "flash" in clean_name or "pro" in clean_name:
                discovered_models.append(clean_name)
    except Exception:
        pass

    # Order of models to attempt
    candidate_models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash"] + discovered_models
    candidate_models = list(dict.fromkeys(candidate_models))  # Deduplicate

    last_error = None
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MitraRecommendation,
                    temperature=0.7,
                ),
            )
            print(f"✅ Successfully used model: {model_name}\n")
            return MitraRecommendation.model_validate_json(response.text)
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Could not reach any Gemini model. Last error: {last_error}")

if __name__ == "__main__":
    print("🤖 Mitra AI Agent Initialized!\n")
    test_input = "I've been staring at a screen all day, my eyes hurt, and I feel overwhelmed about my deadline."
    print(f"Testing with sample check-in:\n'{test_input}'\n")
    
    result = analyze_vibe_and_recommend(test_input)
    print("--- Mitra's Output ---")
    print(json.dumps(result.model_dump(), indent=2))