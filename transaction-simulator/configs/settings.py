from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Transaction Simulator"
    environment: str = "dev"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_dsn: str = "postgresql+asyncpg://simulator:simulator@postgres:5432/simulator"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    redis_url: str = "redis://redis:6379/0"

    rabbit_exchange: str = "transaction.exchange"
    queue_incoming: str = "transaction.incoming"
    queue_processing: str = "transaction.processing"
    queue_retry_schedule: str = "transaction.retry.schedule"
    queue_retry_delay: str = "transaction.retry"
    queue_failed: str = "transaction.failed"
    queue_reversal: str = "transaction.reversal"

    simulate_success_rate: float = Field(default=0.7, ge=0.0, le=1.0)
    simulate_failure_rate: float = Field(default=0.2, ge=0.0, le=1.0)
    simulate_timeout_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    simulate_delay_rate: float = Field(default=0.15, ge=0.0, le=1.0)
    simulate_duplicate_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    simulate_provider_unavailable_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    simulate_db_failure_rate: float = Field(default=0.02, ge=0.0, le=1.0)

    provider_min_latency_ms: int = 30
    provider_max_latency_ms: int = 2000
    timeout_threshold_ms: int = 3000

    retry_backoffs_seconds: str = "5,15,30"
    retry_lock_ttl_seconds: int = 120
    idempotency_ttl_seconds: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()
