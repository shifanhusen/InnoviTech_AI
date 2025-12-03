"""
Configuration management using environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5001
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_TIMEOUT: int = 120
    
    # Session
    SESSION_TTL_SECONDS: int = 600  # 10 minutes
    MAX_HISTORY_MESSAGES: int = 20
    
    # Scraping
    SCRAPE_TIMEOUT: int = 10
    SCRAPE_MAX_CHARS: int = 5000
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
