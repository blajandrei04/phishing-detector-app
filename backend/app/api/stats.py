from fastapi import APIRouter
from app.models.schemas import StatsResponse

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
def get_stats():
    """Get overall statistics. TODO: compute from database."""
    return StatsResponse(
        total_scans=0,
        phishing_count=0,
        suspicious_count=0,
        legitimate_count=0
    )