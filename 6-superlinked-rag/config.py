from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # CometML config
    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT: str | None = None

    # Embeddings config
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-mpnet-base-v2"

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5673
    RABBITMQ_QUEUE_NAME: str = "default"


settings = Settings()
