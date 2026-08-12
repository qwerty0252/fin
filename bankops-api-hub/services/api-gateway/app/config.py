from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    service_name: str = "api-gateway"

    # Auth
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    api_key_header: str = "X-API-Key"

    # Rate limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst: int = 20

    # Downstream services
    transaction_service_url: str = "http://transaction-service:8001"
    orchestration_service_url: str = "http://orchestration-engine:8003"

    # Redis (for rate limiting state)
    redis_url: str = "redis://redis:6379/0"

    # Observability
    otel_exporter_otlp_endpoint: str = "http://jaeger:4317"


@lru_cache
def get_settings() -> Settings:
    return Settings()
