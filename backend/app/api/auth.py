from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.models.schemas import LoginRequest, Token, UserResponse
from app.core.security import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # Automatically seed the "admin" user for quick testing if it doesn't exist
    if not user and credentials.username == "admin" and credentials.password == "thesis":
        user = User(
            username="admin", 
            email="admin@phishing.app", 
            hashed_password=get_password_hash("thesis")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(db: Session = Depends(get_db)):
    # Note: For full implementations, we'd extract token from headers here.
    # Currently hardcoded to get admin for testing purpose.
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    return user
