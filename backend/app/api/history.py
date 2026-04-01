from fastapi import APIRouter
from app.models.schemas import HistoryCreateRequest

router = APIRouter()

@router.post("/history")
def create_history(payload: HistoryCreateRequest):
    """Save scan to history. TODO: implement DB persistence (Week 5)."""
    return {"message": "history endpoint stub", "payload": payload.model_dump()}

@router.get("/history")
def get_history(user_id: str | None = None):
    """Get scan history. TODO: fetch from database (Week 5)."""
    return {"items": [], "user_id": user_id}