from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ScanHistory
from app.db.models import User
from app.api.auth import get_current_user
from app.models.schemas import StatsResponse

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    base_query = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id)
    total = base_query.count()
    phishing = base_query.filter(ScanHistory.verdict == "phishing").count()
    suspicious = base_query.filter(ScanHistory.verdict == "suspicious").count()
    legitimate = base_query.filter(ScanHistory.verdict == "legitimate").count()

    return StatsResponse(
        total_scans=total,
        phishing_count=phishing,
        suspicious_count=suspicious,
        legitimate_count=legitimate
    )