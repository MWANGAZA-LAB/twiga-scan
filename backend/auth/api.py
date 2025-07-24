from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.database import get_db as get_database

from .dependencies import get_current_user, get_db
from .jwt_handler import create_access_token, get_password_hash, verify_password
from .models import APIKey, User

router = APIRouter()


@router.post("/register")
async def register(
    email: str, password: str, full_name: str, db: Session = Depends(get_database)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password, full_name=full_name)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email,
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database),
):
    """Login user and return access token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }


@router.post("/api-keys")
async def create_api_key(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    """Create a new API key for the current user"""
    api_key = APIKey(user_id=current_user.id, name=name)

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "api_key_id": api_key.id,
        "name": api_key.name,
        "key": api_key.key,
        "created_at": api_key.created_at,
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_database)
):
    """List all API keys for the current user"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [
        {
            "id": key.id,
            "name": key.name,
            "created_at": key.created_at,
            "last_used": key.last_used,
        }
        for key in api_keys
    ]
