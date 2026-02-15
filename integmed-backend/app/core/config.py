"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "IntegMed"
    API_VERSION: str = "v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://integmed:password@localhost:5432/integmed"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://integmed.health"
    ]
    
    # ABDM Gateway
    ABDM_GATEWAY_URL: str = os.getenv(
        "ABDM_GATEWAY_URL",
        "https://dev.abdm.gov.in/gateway"
    )
    ABDM_CLIENT_ID: str = os.getenv("ABDM_CLIENT_ID", "")
    ABDM_CLIENT_SECRET: str = os.getenv("ABDM_CLIENT_SECRET", "")
    
    # HPR Integration
    HPR_API_URL: str = os.getenv(
        "HPR_API_URL",
        "https://hpridsbx.ndhm.gov.in/api"
    )
    
    # File Storage
    S3_BUCKET: str = os.getenv("S3_BUCKET", "integmed-documents")
    AWS_REGION: str = "ap-south-1"  # Mumbai region
    
    # AI Services
    WHISPER_MODEL_PATH: str = "/models/whisper-large-v3-medical"
    MEDICAL_NER_MODEL: str = "/models/medcat-medical-ner"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Database Configuration
"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
