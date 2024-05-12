from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TOKENIZERS_PARALLELISM: str = "false"
    OPENAI_API_KEY: str = ""
    COMET_API_KEY: str = ""
    COMET_WORKSPACE: str = ""
    COMET_PROJECT: str = ""

settings = AppSettings()