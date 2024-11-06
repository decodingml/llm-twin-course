from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = str(Path(__file__).parent.parent.parent)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR, env_file_encoding="utf-8")

    # Embeddings config
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 256
    EMBEDDING_SIZE: int = 384
    EMBEDDING_MODEL_DEVICE: str = "cpu"

    # OpenAI config
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None

    # QdrantDB config
    QDRANT_DATABASE_HOST: str = "localhost"  # Or 'qdrant' if running inside Docker
    QDRANT_DATABASE_PORT: int = 6333

    USE_QDRANT_CLOUD: bool = (
        False  # if True, fill in QDRANT_CLOUD_URL and QDRANT_APIKEY
    )
    QDRANT_CLOUD_URL: str = "str"
    QDRANT_APIKEY: str | None = None

    # RAG config
    TOP_K: int = 5
    KEEP_TOP_K: int = 5
    EXPAND_N_QUERY: int = 5

    # CometML config
    COMET_API_KEY: str
    COMET_WORKSPACE: str
    COMET_PROJECT: str = "llm-twin-course"

    # LLM Model config
    HUGGINGFACE_ACCESS_TOKEN: str | None = None
    MODEL_ID: str = "pauliusztin/LLMTwinLlama-3.1-8B"
    DEPLOYMENT_ENDPOINT_NAME: str = "twin"

    MAX_INPUT_TOKENS: int = 1536  # Max length of input text.
    MAX_TOTAL_TOKENS: int = 2048  # Max length of the generation (including input text).
    MAX_BATCH_TOTAL_TOKENS: int = 2048  # Limits the number of tokens that can be processed in parallel during the generation.

    # AWS Authentication
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None


settings = Settings()
