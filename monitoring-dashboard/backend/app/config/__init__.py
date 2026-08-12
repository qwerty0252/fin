"""Configuration management for the monitoring dashboard"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import logging


class Settings(BaseSettings):
    """Application settings"""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/monitoring_dashboard"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Observability
    log_level: str = "INFO"
    jaeger_enabled: bool = True
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831

    # Alerts
    alert_enabled: bool = True
    alert_email_smtp_host: str = "smtp.gmail.com"
    alert_email_smtp_port: int = 587
    alert_email_from: str = "noreply@bankops.local"
    slack_webhook_url: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
