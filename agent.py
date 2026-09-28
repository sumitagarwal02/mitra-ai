import time
import os
import google.generativeai as genai
from pydantic import BaseModel, Field

# Ensure API Key is set
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class VibeRecommendation(BaseModel):
    mood_analysis: str = Field(description="Empathetic, deep reflection on the user's check-in")
    micro_exercise: str = Field(description="A quick 1-2 minute sensory reset exercise")
    journal_prompt: str = Field(description="A reflective journal prompt for further exploration")
    youtube_search_query: str = Field(description="Targeted YouTube search query for calming ambient audio")
    stress_level: int = Field(description="Estimated stress level from 1 (lowest) to 10 (highest)")
    energy_level: int = Field(description="Estimated energy level from 1 (lowest) to 10 (highest)")
    dominant_emotion: str = Field(description="Single dominant emotion word, e.g., Anxious, Calm, Exhausted")

def analyze_vibe_and_recommend(user_input: str, rag_context: str = "", max_retries: int = 3) -> VibeRecommendation:
    """
    Analyzes user check-in with automatic retry logic and fallback models 
    to handle transient 503 UNAVAILABLE errors gracefully.
    """
    # Models to try in order of preference
    models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    
    prompt_text = f"""
    You are Mitra, a compassionate and perceptive AI wellness companion.
    
    Past Context:
    {rag_context}
    
    User Check-in:
    {user_input}
    
    Analyze the user's current vibe, estimate stress and energy levels (1-10), identify the dominant emotion,
    and provide an empathetic reflection, a micro reset exercise, a journal prompt, and a soundscape search query.
    """

    last_exception = None

    for model_name in models_to_try:
        model = genai.GenerativeModel(model_name)
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    prompt_text,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=VibeRecommendation
                    )
                )
                # Parse structured JSON output
                return VibeRecommendation.model_validate_json(response.text)
                
            except Exception as e:
                error_str = str(e)
                last_exception = e
                # Check for 503 UNAVAILABLE or rate limit
                if "503" in error_str or "UNAVAILABLE" in error_str or "429" in error_str:
                    wait_time = (attempt + 1) * 2  # Exponential backoff (2s, 4s, 6s)
                    time.sleep(wait_time)
                else:
                    # Non-503 error, break inner loop to try next model fallback
                    break

    # If all models and retries fail, raise a clean error message
    raise RuntimeError(
        "The AI model service is currently experiencing high demand. Please try sending your message again in a few seconds."
    )