from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=True, index=True)
    public_key = Column(String(255), nullable=True, index=True)
    certificate_fingerprint = Column(String(255), nullable=True)
    api_url = Column(String(500), nullable=True)
    provider_type = Column(String(100), nullable=False)  # wallet, exchange, etc.
    status = Column(String(50), default="trusted")  # trusted, suspicious, blocked
    provider_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
