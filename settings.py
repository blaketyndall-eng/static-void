from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Decision Intelligence Console API", alias="APP_NAME")
    app_env: Literal["development", "test", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    cors_origins: list[str] = Field(default_factory=list, alias="CORS_ORIGINS")


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
