import os
import time
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class VibeResponse(BaseModel):
    mood_analysis: str = Field(
        description="A deep, highly creative, and empathetic exploration of the user's feelings using vivid imagery, comforting metaphors, and rich validation across 2-3 descriptive paragraphs."
    )
    micro_exercise: str = Field(
        description="An imaginative, step-by-step somatic reset or guided visualization exercise that deeply engages all five senses."
    )
    journal_prompt: str = Field(
        description="Two evocative, deep reflection prompts for creative self-discovery and expressive storytelling."
    )
    youtube_search_query: str = Field(
        description="A specific search term for ambient soundscapes, guided meditation, or therapeutic music."
    )

def analyze_vibe_and_recommend(user_input, rag_context: str = "") -> VibeResponse:
    print("--> Starting Gemini API Request...")
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_instruction = """
    You are Mitra, an extraordinarily intuitive, warm, and poetic AI wellness companion.
    Your goal is to offer rich, descriptive, and imaginative support:
    - If input is audio, listen carefully to what the user said and address their spoken feelings with deep care.
    - Avoid brief or superficial advice. Paint vivid mental images, use gentle metaphors, and explore feelings with depth and warmth.
    - Craft sensory-rich somatic resets (guided visualizations, deep breathing with imagery, sensory grounding).
    - Maintain a deeply comforting, non-clinical tone that feels like a wise, compassionate friend.
    - Subtly weave in relevant past memory patterns if RAG context is provided.
    """

    contents = []
    if isinstance(user_input, bytes):
        contents.append(
            types.Part.from_bytes(
                data=user_input,
                mime_type="audio/wav"
            )
        )
        contents.append(f"Listen to this audio voice check-in and respond.\nRelevant Semantic Memory (Past RAG Context): {rag_context}")
    else:
        contents.append(f"User Current Input: {user_input}\nRelevant Semantic Memory (Past RAG Context): {rag_context}")

    model_name = "gemini-3.6-flash"
    
    for attempt in range(2):
        try:
            print(f"--> Attempt {attempt + 1}: Calling {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=VibeResponse,
                    temperature=0.85,
                )
            )
            print("--> Response received successfully!")
            return VibeResponse.model_validate_json(response.text)
        except Exception as e:
            print(f"--> Error on attempt {attempt + 1}: {str(e)}")
            if attempt < 1:
                time.sleep(2)
            else:
                raise e