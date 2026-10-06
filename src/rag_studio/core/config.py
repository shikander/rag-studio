"""App settings, read from environment variables or a .env file in the working directory."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    generator: Literal["llm", "mock"] = "llm"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    fast_model: str = "meta-llama/llama-3.3-70b-instruct"
    strong_model: str = "qwen/qwen-2.5-coder-32b-instruct"
    llm_timeout_seconds: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()