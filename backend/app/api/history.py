from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.db.models import ScanHistory
from app.models.schemas import HistoryCreateRequest

router = APIRouter()

@router.post("/history")
def create_history(payload: HistoryCreateRequest, db: Session = Depends(get_db)):
    return {"message": "handled by analyze endpoint mostly"}

@router.get("/history")
def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    verdict: str | None = None,
    search: str | None = None,
    user_id: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(ScanHistory)
    
    # Apply filtering
    if verdict and verdict.lower() != "all":
        query = query.filter(ScanHistory.verdict == verdict.lower())
        
    if search:
        query = query.filter(ScanHistory.url.ilike(f"%{search}%"))
        
    # Get total count for pagination math on frontend
    total_count = query.count()
    
    # Apply sorting and pagination
    scans = query.order_by(ScanHistory.scanned_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for scan in scans:
        results.append({
            "id": scan.id,
            "url": scan.url,
            "score": scan.score,
            "verdict": scan.verdict,
            "created_at": scan.scanned_at
        })
        
    return {
        "items": results,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }