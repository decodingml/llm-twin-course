from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    # Embeddings config
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 256
    EMBEDDING_SIZE: int = 384
    EMBEDDING_MODEL_DEVICE: str = "cpu"

    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None

    # MongoDB configs
    MONGO_DATABASE_HOST: str = "mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set"
    MONGO_DATABASE_NAME: str = "scrabble"

    # QdrantDB config
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_DATABASE_URL: str = "http://localhost:6333"
    QDRANT_CLOUD_URL: str = "str"
    USE_QDRANT_CLOUD: bool = False
    QDRANT_APIKEY: str | None = None

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5673

    # CometML config
    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT: str | None = None

    # LinkedIn credentials
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None

    # LLM Model config
    TOKENIZERS_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str | None = None
    MODEL_TYPE: str = "mistralai/Mistral-7B-Instruct-v0.1"

    QWAK_DEPLOYMENT_MODEL_ID: str = "copywriter_model"
    QWAK_DEPLOYMENT_MODEL_API: str = (
        "https://models.llm-twin.qwak.ai/v1/copywriter_model/default/predict"
    )


settings = AppSettings()
