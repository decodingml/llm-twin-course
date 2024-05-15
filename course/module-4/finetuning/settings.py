from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict()

    TOKENIZERS_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str = ""
    COMET_API_KEY: str = ""
    COMET_WORKSPACE: str = ""
    COMET_PROJECT: str = ""

settings = AppSettings()