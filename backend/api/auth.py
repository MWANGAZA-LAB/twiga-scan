from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
)
from auth.jwt_handler import (
    create_user_tokens,
    generate_api_key,
    get_password_hash,
    hash_api_key,
    verify_password,
)
from auth.models import (
    APIKey,
    APIKeyCreate,
    APIKeyResponse,
    Token,
    User,
    UserCreate,
    UserResponse,
)
from models.database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    existing_username = (
        db.query(User).filter(User.username == user_data.username).first()
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login user and return access token"""
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    tokens = create_user_tokens(user.id, user.username)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new API key for the current user"""
    # Generate API key
    api_key = generate_api_key()
    hashed_key = hash_api_key(api_key)

    # Store in database
    db_api_key = APIKey(
        user_id=current_user.id,
        key_name=api_key_data.key_name,
        key_hash=hashed_key,
        permissions=api_key_data.permissions,
        expires_at=api_key_data.expires_at,
    )

    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)

    # Return the API key (only shown once)
    response = APIKeyResponse(
        id=db_api_key.id,
        key_name=db_api_key.key_name,
        permissions=api_key_data.permissions,
        is_active=db_api_key.is_active,
        created_at=db_api_key.created_at,
        last_used=db_api_key.last_used,
        expires_at=db_api_key.expires_at,
    )

    # Include the actual API key in response (only for creation)
    response.api_key = api_key

    return response


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """List all API keys for the current user"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

    return api_keys


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Revoke an API key"""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    api_key.is_active = False
    db.commit()

    return {"message": "API key revoked successfully"}


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    from auth.jwt_handler import verify_token
    
    # Verify the refresh token
    token_data = verify_token(refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create new tokens
    new_tokens = create_user_tokens(user.id, user.username)
    return new_tokens
