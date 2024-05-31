from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TOKENIZERS_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str = ""
    COMET_API_KEY: str = ""
    COMET_WORKSPACE: str = ""
    COMET_PROJECT: str = ""
    
    CACHE_DIR: Path = Path("./cache")

settings = AppSettings()