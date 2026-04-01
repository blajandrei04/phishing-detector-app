from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()

@router.get("/test", response_model=HealthResponse)
def test_api():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        app="phishing-detector-api",
        version="0.1.0"
    )