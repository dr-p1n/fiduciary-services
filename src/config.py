"""
Configuration Management

Centralized configuration management for the AGENTTA application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    debug: bool = False

    # Database
    database_url: str = "postgresql://agentta:password@localhost:5432/agentta_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # AI Services
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Security
    secret_key: str = "change-me-in-production"
    encryption_master_key: Optional[str] = None
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "noreply@agentta.com"

    # Application
    app_name: str = "AGENTTA"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/agentta.log"

    # Feature Flags
    enable_ai_processing: bool = True
    enable_email_integration: bool = True
    enable_calendar_sync: bool = True
    enable_document_ocr: bool = False

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50
    allowed_file_types: str = "pdf,docx,doc,txt,xlsx,xls,msg,eml"

    # Monitoring
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins_list(self) -> list:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_allowed_file_types_list(self) -> list:
        """Get allowed file types as a list."""
        return [ft.strip() for ft in self.allowed_file_types.split(",")]

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()


# Convenience function to get settings
settings = get_settings()
