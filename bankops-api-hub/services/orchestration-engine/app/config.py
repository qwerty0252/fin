from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    service_name: str = "orchestration-engine"

    connector_service_url: str = "http://connector-framework:8004"
    transaction_service_url: str = "http://transaction-service:8001"
    notification_service_url: str = "http://notification-service:8005"
    event_bus_url: str = "http://event-bus:8002"
    rabbitmq_url: str = "amqp://bankops:bankops@rabbitmq:5672/bankops"

    # Timeouts (seconds)
    step_timeout: int = 30
    workflow_timeout: int = 120
    max_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
