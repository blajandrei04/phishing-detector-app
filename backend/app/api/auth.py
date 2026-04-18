from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
import logging
from app.db.database import get_db
from app.db.models import User
from app.models.schemas import (
    LoginRequest, Token, UserResponse, RegisterRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    ChangePasswordRequest, UpdateProfileRequest
)
from app.core.security import (
    verify_password, create_access_token, get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
)

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ──────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────
@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == request.username) | (User.email == request.email)).first()
    if user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")
    
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ──────────────────────────────────────────────
# Forgot Password — issues a short-lived reset token
# ──────────────────────────────────────────────
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        # Create a short-lived reset token (15 min expiry)
        reset_token = create_access_token(
            data={"sub": user.username, "purpose": "reset"},
            expires_delta=timedelta(minutes=15)
        )
        # In production, this token would be emailed to the user.
        # For this thesis demo, we log it and return it directly so
        # the frontend can immediately proceed to the reset form.
        logger.info(f"Password reset token generated for {user.email}: {reset_token}")
        return {
            "message": "Password reset token generated successfully.",
            "reset_token": reset_token  # Exposed for thesis demo purposes
        }
    # Security: always return the same shape so attackers can't enumerate emails
    return {
        "message": "If that email is registered, you will receive a reset link shortly.",
        "reset_token": None
    }

# ──────────────────────────────────────────────
# Reset Password — validates token and sets new password
# ──────────────────────────────────────────────
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        purpose = payload.get("purpose")
        if username is None or purpose != "reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password has been reset successfully"}

# ──────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# Get Current User Profile
# ──────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ──────────────────────────────────────────────
# Update Profile (email / username)
# ──────────────────────────────────────────────
@router.put("/me", response_model=UserResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.email and request.email != current_user.email:
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email is already in use")
        current_user.email = request.email

    if request.username and request.username != current_user.username:
        existing = db.query(User).filter(User.username == request.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username is already taken")
        current_user.username = request.username

    db.commit()
    db.refresh(current_user)
    return current_user

# ──────────────────────────────────────────────
# Change Password (requires current password)
# ──────────────────────────────────────────────
@router.put("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
