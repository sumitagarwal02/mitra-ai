import os
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class VibeResponse(BaseModel):
    mood_analysis: str = Field(description="Empathetic 2-3 sentence validation of how the user is feeling.")
    micro_exercise: str = Field(description="A quick 2-minute actionable somatic or mental reset exercise.")
    journal_prompt: str = Field(description="A gentle reflection or journaling question for deep thought.")
    youtube_search_query: str = Field(description="A specific search term for YouTube practice/meditation/breathwork.")

def analyze_vibe_and_recommend(user_input: str, rag_context: str = "") -> VibeResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_instruction = """
    You are Mitra, a warm, highly empathetic, conversational wellness companion.
    Your job is to listen, validate feelings gently, and offer immediate, low-friction micro-resets.
    Never mention job interviews, exams, or clinical medical diagnoses. Speak directly to the user as a supportive friend.
    If relevant past memory context is provided, subtly weave it into your assessment to show deep active listening.
    """

    prompt = f"""
    User Current Input: {user_input}

    Relevant Semantic Memory (Past RAG Context):
    {rag_context}

    Based on their current input and past memory patterns, provide a compassionate mood assessment, a 2-minute micro-reset, a journal prompt, and a YouTube search query.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=VibeResponse,
            temperature=0.7,
        )
    )

    return VibeResponse.model_validate_json(response.text)