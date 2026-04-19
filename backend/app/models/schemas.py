from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    user_id: Optional[str]= None

class AnalyzeResponse(BaseModel):
    url: str
    score: float = Field(ge=0.0, le=1.0)
    verdict: str
    confidence: float = Field(ge=0.0, le=1.0)
    extracted_features: Optional[Dict[str, Any]] = None
    shap_explanation: Optional[Dict[str, Any]] = None
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    app: str
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
    