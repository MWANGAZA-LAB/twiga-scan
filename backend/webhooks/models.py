from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..models.database import Base


class Webhook(Base):
    """Webhook configuration model"""
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)  # List of event types
    secret = Column(String, nullable=True)  # Webhook secret for verification
    is_active = Column(Boolean, default=True)
    retry_count = Column(Integer, default=0)
    last_delivery = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WebhookDelivery(Base):
    """Webhook delivery log"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    delivery_time = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)


# Pydantic models
class WebhookCreate(BaseModel):
    name: str
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: int
    name: str
    url: str
    events: List[str]
    is_active: bool
    retry_count: int
    last_delivery: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    id: int
    webhook_id: int
    event_type: str
    payload: Dict[str, Any]
    response_status: Optional[int] = None
    success: bool
    delivery_time: datetime
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


# Event types
WEBHOOK_EVENTS = {
    "scan.created": "Triggered when a new scan is created",
    "scan.verified": "Triggered when a scan is verified",
    "scan.failed": "Triggered when a scan fails",
    "user.registered": "Triggered when a new user registers",
    "user.login": "Triggered when a user logs in",
    "api_key.created": "Triggered when an API key is created",
    "api_key.revoked": "Triggered when an API key is revoked",
    "provider.added": "Triggered when a new provider is added",
    "provider.verified": "Triggered when a provider is verified",
}


class WebhookPayload(BaseModel):
    """Standard webhook payload format"""
    event: str
    timestamp: datetime
    data: Dict[str, Any]
    webhook_id: int
    
    def to_json(self) -> str:
        """Convert payload to JSON string"""
        return json.dumps(self.dict(), default=str) 