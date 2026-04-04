from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import ScanHistory
from typing import List, Dict

def save_scan(db: Session, scan_data: dict, user_id: int = None) -> ScanHistory:
    """Save a phishing scan to database."""
    db_scan = ScanHistory(
        url=scan_data.get("url"),
        score=scan_data.get("score"),
        verdict=scan_data.get("verdict"),
        user_id=user_id
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

def get_scan_history(db: Session, user_id: int | None = None) -> List[ScanHistory]:
    """Retrieve scan history for user or all history if not specified."""
    query = db.query(ScanHistory)
    if user_id:
        query = query.filter(ScanHistory.user_id == user_id)
    return query.order_by(ScanHistory.scanned_at.desc()).all()

def get_stats(db: Session) -> Dict:
    """Get overall statistics."""
    total_scans = db.query(func.count(ScanHistory.id)).scalar()
    phishing_count = db.query(func.count(ScanHistory.id)).filter(ScanHistory.verdict == "phishing").scalar()
    suspicious_count = db.query(func.count(ScanHistory.id)).filter(ScanHistory.verdict == "suspicious").scalar()
    legitimate_count = db.query(func.count(ScanHistory.id)).filter(ScanHistory.verdict == "legitimate").scalar()

    return {
        "total_scans": total_scans,
        "phishing_count": phishing_count,
        "suspicious_count": suspicious_count,
        "legitimate_count": legitimate_count
    }