from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    user_id: Optional[str]= None

class AnalyzeResponse(BaseModel):
    url: str
    score: float = Field(ge=0.0, le=1.0)
    verdict: str
    confidence: float = Field(ge=0.0, le=1.0)
    extracted_features: Optional[Dict[str, Any]] = None
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    app: float
    version: str

class HistoryCreateRequest(BaseModel):
    url: HttpUrl
    score: float
    verdict: str
    user_id: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    url: str
    score: float
    verdict: str
    created_at: datetime

class StatsResponse(BaseModel):
    total_scans: int
    phishing_count: int
    legitimate_count: int
    suspicious_count: int
    