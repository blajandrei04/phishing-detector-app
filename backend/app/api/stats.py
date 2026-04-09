from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ScanHistory
from app.models.schemas import StatsResponse

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(ScanHistory).count()
    phishing = db.query(ScanHistory).filter(ScanHistory.verdict == "phishing").count()
    suspicious = db.query(ScanHistory).filter(ScanHistory.verdict == "suspicious").count()
    legitimate = db.query(ScanHistory).filter(ScanHistory.verdict == "legitimate").count()

    return StatsResponse(
        total_scans=total,
        phishing_count=phishing,
        suspicious_count=suspicious,
        legitimate_count=legitimate
    )