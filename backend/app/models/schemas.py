from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator('username')
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v

    @field_validator('email')
    @classmethod
    def email_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Please enter a valid email address')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=255)

    @field_validator('email')
    @classmethod
    def email_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Please enter a valid email address')
        return v

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=6, max_length=128)

    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)

    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UpdateProfileRequest(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator('email')
    @classmethod
    def email_valid(cls, v):
        if v is None:
            return v
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Please enter a valid email address')
        return v

    @field_validator('username')
    @classmethod
    def username_valid(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    user_id: Optional[str] = None

    @field_validator('url')
    @classmethod
    def url_length_check(cls, v):
        url_str = str(v)
        if len(url_str) > 2048:
            raise ValueError('URL must be shorter than 2048 characters')
        return v

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

class FeedbackCreate(BaseModel):
    url: HttpUrl
    original_verdict: str
    user_reported_verdict: str
    comments: Optional[str] = None
    user_id: Optional[str] = None
    