from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    chroma_persist_directory: str = "/chroma_data"
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    llm_provider: str = "groq"  # groq, ollama or openai
    ollama_url: str = "http://localhost:11434"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
