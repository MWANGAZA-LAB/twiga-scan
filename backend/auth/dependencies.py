from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..models.database import get_db
from .jwt_handler import verify_api_key, verify_token
from .models import APIKey, TokenData, User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


def get_user_by_api_key(api_key: str, db: Session = Depends(get_db)) -> Optional[User]:
    """Get user by API key"""
    # Check if it's a valid API key format
    if not api_key.startswith("twiga_"):
        return None

    # Find the API key in database
    db_api_key = (
        db.query(APIKey)
        .filter(APIKey.is_active is True)
        .filter(APIKey.key_hash == api_key)  # This should be hashed comparison
        .first()
    )

    if not db_api_key:
        return None

    # Get the user
    user = db.query(User).filter(User.id == db_api_key.user_id).first()
    if not user or not user.is_active:
        return None

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def require_permission(permission: str):
    """Decorator to require specific permission"""

    def permission_checker(current_user: User = Depends(get_current_user)):
        # For now, only superusers have all permissions
        # TODO: Implement proper permission system
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return current_user

    return permission_checker
