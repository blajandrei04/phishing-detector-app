from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.db.models import ScanHistory, Feedback
from app.db.models import User
from app.models.schemas import HistoryCreateRequest, FeedbackCreate, FeedbackResponse
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/feedback")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_feedback = Feedback(
        url=str(payload.url),
        original_verdict=payload.original_verdict,
        user_reported_verdict=payload.user_reported_verdict,
        comments=payload.comments,
        user_id=current_user.id
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return {"message": "Feedback submitted successfully", "id": db_feedback.id}

@router.get("/feedback", response_model=list[FeedbackResponse])
def get_all_feedback(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from fastapi import HTTPException
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return db.query(Feedback).order_by(Feedback.reported_at.desc()).all()

@router.delete("/feedback/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from fastapi import HTTPException
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(fb)
    db.commit()
    return {"message": "Feedback deleted successfully"}

import csv
import os
import subprocess
from fastapi import BackgroundTasks

# Simple counter for demo purposes
retrain_counter = 0
RETRAIN_THRESHOLD = 3

def trigger_retraining():
    print("Triggering background MLOps retraining pipeline...")
    # Run the training script in the background
    # It will save the new model to artifacts/xgb_opt.pkl
    subprocess.run(["python", "train_model.py"], check=False)
    # Once it finishes, the model loader would need to reload it, 
    # but for this demo, the file is overwritten on disk.
    print("Background retraining complete.")

@router.post("/feedback/{feedback_id}/acknowledge")
def acknowledge_feedback(
    feedback_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    global retrain_counter
    from fastapi import HTTPException
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
        
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    # Map verdict to CSV label ('bad' or 'good')
    label = "bad" if fb.user_reported_verdict in ["phishing", "suspicious"] else "good"
    
    # Append to dataset
    dataset_path = "datasets/phishing_site_urls.csv"
    if os.path.exists(dataset_path):
        with open(dataset_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([fb.url, label])
            
    # Delete the feedback from the queue
    db.delete(fb)
    db.commit()
    
    retrain_counter += 1
    triggered = False
    
    # Trigger MLOps pipeline if threshold met
    if retrain_counter >= RETRAIN_THRESHOLD:
        background_tasks.add_task(trigger_retraining)
        retrain_counter = 0
        triggered = True
        
    return {
        "message": "Feedback acknowledged, added to dataset.", 
        "retrain_triggered": triggered
    }


@router.post("/history")
def create_history(payload: HistoryCreateRequest, db: Session = Depends(get_db)):
    return {"message": "handled by analyze endpoint mostly"}

@router.get("/history")
def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    verdict: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id)
    
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