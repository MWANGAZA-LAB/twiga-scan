import enum

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class AuthStatus(str, enum.Enum):
    VERIFIED = "Verified"
    SUSPICIOUS = "Suspicious"
    INVALID = "Invalid"


class ContentType(str, enum.Enum):
    BIP21 = "BIP21"
    BOLT11 = "BOLT11"
    LNURL = "LNURL"
    LIGHTNING_ADDRESS = "LIGHTNING_ADDRESS"
    UNKNOWN = "UNKNOWN"


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), unique=True, index=True)  # UUID
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    raw_content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    parsed_data = Column(JSON, nullable=True)
    provider = Column(String(255), nullable=True)
    auth_status = Column(Enum(AuthStatus), nullable=False)
    verification_results = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    user_action = Column(String(50), nullable=True)  # approved, aborted, etc.
    outcome = Column(String(255), nullable=True)
    device_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    normalized_identifier = Column(
        String(500), index=True, nullable=True
    )  # Normalized address/invoice for duplicate detection
    first_seen = Column(
        DateTime(timezone=True), nullable=True
    )  # First time this identifier was seen
    usage_count = Column(
        Integer, default=1, nullable=False
    )  # Number of times scanned
