from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MongoDB
    DATABASE_HOST: str = "mongodb://scrabble:scrabble@localhost:27018"
    DATABASE_NAME: str = "scrabble"

    # LinkedIn Credentials
    LINKEDIN_USERNAME: Optional[str] = None
    LINKEDIN_PASSWORD: Optional[str] = None


settings = Settings()
