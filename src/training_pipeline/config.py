from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = str(Path(__file__).parent.parent.parent.parent)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR, env_file_encoding="utf-8")

    HUGGINGFACE_ACCESS_TOKEN: str = ""

    COMET_API_KEY: str = ""
    COMET_WORKSPACE: str = ""
    COMET_PROJECT: str = ""

    DATASET_ARTIFACT_NAME: str = "posts-instruct-dataset"

    # AWS Authentication
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None


settings = Settings()
