from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import analyze_vibe_and_recommend, MitraRecommendation

app = FastAPI(
    title="Mitra AI - Wellness Companion API",
    description="Backend API powering Mitra's adaptive vibe checks and tailored recommendations.",
    version="1.0.0"
)

class CheckInRequest(BaseModel):
    user_input: str

@app.get("/health")
def health_check():
    """Returns the API service health status."""
    return {"status": "healthy", "agent": "Mitra AI Ready"}

@app.post("/api/checkin", response_model=MitraRecommendation)
def process_checkin(request: CheckInRequest):
    """Processes user vibe check-in responses and generates recommendations."""
    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="Check-in text cannot be empty.")
    try:
        recommendation = analyze_vibe_and_recommend(request.user_input)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")