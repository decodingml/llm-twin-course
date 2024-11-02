from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = str(Path(__file__).parent.parent.parent.parent)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR, env_file_encoding="utf-8")

    TOKENIZERS_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str = ""
    COMET_API_KEY: str = ""
    COMET_WORKSPACE: str = ""
    COMET_PROJECT: str = ""

    DATASET_ARTIFACT_NAME: str = "posts-instruct-dataset"
    FINE_TUNED_LLM_TWIN_MODEL_TYPE: str = "decodingml/llm-twin:1.0.0"
    CONFIG_FILE: str = "./finetuning/config.yaml"

    MODEL_SAVE_DIR: str = "./training_pipeline_output"
    CACHE_DIR: Path = Path("./.cache")


settings = Settings()
print(settings)
