from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
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


@router.get("/stats/activity")
def get_scan_activity(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns daily scan counts for the past N days, broken down by verdict."""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    # Use func.date() for SQLite compatibility (stores dates as text)
    rows = (
        db.query(
            func.date(ScanHistory.scanned_at).label("scan_date"),
            ScanHistory.verdict,
            func.count().label("count")
        )
        .filter(
            ScanHistory.user_id == current_user.id,
            ScanHistory.scanned_at >= start_date
        )
        .group_by(func.date(ScanHistory.scanned_at), ScanHistory.verdict)
        .all()
    )

    # Build a dict of date -> {phishing, legitimate, suspicious, total}
    day_map = {}
    for i in range(days):
        d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        day_map[d] = {"date": d, "phishing": 0, "legitimate": 0, "suspicious": 0, "total": 0}

    for row in rows:
        d = str(row.scan_date)  # func.date() returns string in SQLite
        if d in day_map:
            day_map[d][row.verdict] = row.count
            day_map[d]["total"] += row.count

    activity = list(day_map.values())
    max_total = max((d["total"] for d in activity), default=1) or 1

    return {
        "days": activity,
        "max_daily": max_total
    }