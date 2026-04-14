from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScanHistory(Base):
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional for MVP
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())
