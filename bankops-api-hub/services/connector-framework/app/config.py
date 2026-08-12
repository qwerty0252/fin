from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    service_name: str = "connector-framework"

    mock_switch_enabled: bool = True
    mock_switch_failure_rate: float = 0.05


@lru_cache
def get_settings() -> Settings:
    return Settings()
