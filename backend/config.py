from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Twiga Scan"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./twiga_scan.db"  # Set in .env for production

    # Redis
    REDIS_URL: Optional[str] = None  # Set in .env for production

    # Security
    SECRET_KEY: str = (
        "dev-secret-key-change-in-production"  # Set in .env for production
    )
    JWT_SECRET_KEY: str = (
        "dev-jwt-secret-key-change-in-production"  # Set in .env for production
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Logging
    LOG_LEVEL: str = "info"

    # Bitcoin/Lightning
    BITCOIN_NETWORK: str = "mainnet"
    LIGHTNING_NETWORK: str = "mainnet"

    # External APIs
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]

    # Monitoring
    SENTRY_DSN: Optional[str] = None  # Set in .env for production
    PROMETHEUS_ENABLED: bool = False

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("ALLOWED_FILE_TYPES", pre=True)
    def assemble_file_types(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
