from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    service_name: str = "notification-service"

    slack_webhook_url: str = ""
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alerts_email: str = ""

    rabbitmq_url: str = "amqp://bankops:bankops@rabbitmq:5672/bankops"
    notification_queue: str = "bankops.notifications"


@lru_cache
def get_settings() -> Settings:
    return Settings()
