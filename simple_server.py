#!/usr/bin/env python3
"""
Simple Twiga Scan API Server for testing
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

# Pydantic models
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class APIKeyCreate(BaseModel):
    name: str

# Create FastAPI app
app = FastAPI(
    title="Twiga Scan API",
    description="Bitcoin/Lightning QR & URL Authentication Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
users_db = {}
api_keys_db = {}

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(token: str = Depends(OAuth2PasswordRequestForm)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if email not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        return users_db[email]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "twiga-scan-api",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Twiga Scan API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Authentication endpoints
@app.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_db[user_data.email] = user
    
    return {
        "message": "User registered successfully",
        "email": user_data.email
    }

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user["email"]
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }

@app.post("/auth/api-keys")
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new API key for the current user"""
    api_key = {
        "id": len(api_keys_db) + 1,
        "user_email": current_user["email"],
        "name": api_key_data.name,
        "key": f"twiga_{secrets.token_urlsafe(32)}",
        "created_at": datetime.utcnow()
    }
    
    api_keys_db[api_key["id"]] = api_key
    
    return {
        "api_key_id": api_key["id"],
        "name": api_key["name"],
        "key": api_key["key"],
        "created_at": api_key["created_at"]
    }

@app.get("/auth/api-keys")
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """List all API keys for the current user"""
    user_keys = [
        {
            "id": key["id"],
            "name": key["name"],
            "created_at": key["created_at"]
        }
        for key in api_keys_db.values()
        if key["user_email"] == current_user["email"]
    ]
    return user_keys

# Monitoring endpoints
@app.get("/metrics")
async def get_metrics():
    """Get basic metrics"""
    return {
        "total_users": len(users_db),
        "total_api_keys": len(api_keys_db),
        "uptime": time.time(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Twiga Scan API Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 