from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "enterprise-multitool-agent-platform"
    version: str = "0.1.0"
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg://agent:agent@postgres:5432/agent_platform"
    redis_url: str = "redis://redis:6379/0"

    jwt_secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    deepseek_api_key: str | None = None
    default_llm_provider: str = "mock"
    default_embedding_provider: str = "mock"
    vector_dimension: int = 1536

    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"
    demo_mode: bool = False
    run_migrations_on_start: bool = True
    seed_demo_on_start: bool = False
    frontend_origin: str = "http://localhost:3100"

    cors_origins: list[AnyHttpUrl | str] = [
        "http://localhost:3100",
        "http://127.0.0.1:3100",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
