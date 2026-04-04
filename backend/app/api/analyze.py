from datetime import datetime, timezone
from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.feature_extractor import extract_features
from app.services.model_loader import ModelLoader
from app.core.config import settings


router = APIRouter()

model_loader = ModelLoader(settings.model_path)
model_loader.load()


def _verdict_from_score(score: float) -> str:
    if score >= 0.70:
        return "phishing"
    if score >= 0.40:
        return "suspicious"
    return "legitimate"


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(payload: AnalyzeRequest):
    features = extract_features(str(payload.url))
    score = model_loader.predict_score(features)
    score = max(0.0, min(1.0, score))  # clamp to [0, 1]
    verdict = _verdict_from_score(score)

    # Simple confidence heuristic for now
    confidence = max(0.5, abs(score - 0.5) * 2)

    return AnalyzeResponse(
        url=str(payload.url),
        score=score,
        verdict=verdict,
        confidence=confidence,
        extracted_features=features,
        timestamp=datetime.now(timezone.utc),
    )