from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    service_name: str = "event-bus"

    rabbitmq_url: str = "amqp://bankops:bankops@rabbitmq:5672/bankops"

    # Queue configuration
    default_exchange: str = "bankops.events"
    dead_letter_exchange: str = "bankops.dlx"
    dead_letter_queue: str = "bankops.dead_letters"
    max_retry_count: int = 3
    retry_delay_ms: int = 5000

    # Queues
    transaction_queue: str = "bankops.transactions"
    notification_queue: str = "bankops.notifications"
    orchestration_queue: str = "bankops.orchestration"


@lru_cache
def get_settings() -> Settings:
    return Settings()
