import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ethara Seat Allocation System"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///ethara.db")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    
    # Pydantic Settings configuration (V2 style)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
