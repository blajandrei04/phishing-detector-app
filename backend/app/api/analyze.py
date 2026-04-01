from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.feature_extractor import extract_features

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(payload: AnalyzeRequest):
    """Analyze URL for phishing likelihood."""
    features = extract_features(str(payload.url))

    # TODO: replace with real model score
    score = 0.42

    if score >= 0.70:
        verdict = "phishing"
    elif score >= 0.40:
        verdict = "suspicious"
    else:
        verdict = "legitimate"

    return AnalyzeResponse(
        url=str(payload.url),
        score=score,
        verdict=verdict,
        confidence=0.75,
        extracted_features=features,
        timestamp=datetime.utcnow()
    )