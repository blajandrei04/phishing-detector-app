from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ScanHistory
from app.models.schemas import HistoryCreateRequest

router = APIRouter()

@router.post("/history")
def create_history(payload: HistoryCreateRequest, db: Session = Depends(get_db)):
    return {"message": "handled by analyze endpoint mostly"}

@router.get("/history")
def get_history(user_id: str | None = None, db: Session = Depends(get_db)):
    scans = db.query(ScanHistory).order_by(ScanHistory.scanned_at.desc()).limit(10).all()
    results = []
    for scan in scans:
        results.append({
            "id": scan.id,
            "url": scan.url,
            "score": scan.score,
            "verdict": scan.verdict,
            "created_at": scan.scanned_at
        })
    return {"items": results, "user_id": user_id}