from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    service_name: str = "transaction-service"

    database_url: str = "postgresql+asyncpg://bankops:bankops@postgres:5432/bankops"
    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = "amqp://bankops:bankops@rabbitmq:5672/bankops"

    event_bus_url: str = "http://event-bus:8002"
    orchestration_service_url: str = "http://orchestration-engine:8003"


@lru_cache
def get_settings() -> Settings:
    return Settings()
