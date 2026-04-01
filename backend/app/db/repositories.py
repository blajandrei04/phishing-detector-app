"""
Database repositories for CRUD operations.
TODO: implement SQLAlchemy models and DB operations in Week 5
"""

def save_scan(scan_data: dict) -> dict:
    """Save a phishing scan to database."""
    return {"saved": False, "reason": "not implemented"}

def get_scan_history(user_id: str | None = None) -> list[dict]:
    """Retrieve scan history for user."""
    return []

def get_stats() -> dict:
    """Get overall statistics."""
    return {
        "total_scans": 0,
        "phishing_count": 0,
        "suspicious_count": 0,
        "legitimate_count": 0
    }