from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Embeddings config
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-mpnet-base-v2"

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_QUEUE_NAME: str = "default"
    
    # Superlinked
    SUPERLINKED_SERVER_URL: str = "http://localhost:8080"


settings = Settings()
