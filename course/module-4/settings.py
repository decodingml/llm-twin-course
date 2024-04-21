from typing import Optional
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):

    # Embeddings config
    EMBEDDING_MODEL_ID: str = 'sentence-transformers/all-MiniLM-L6-v2'
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 256
    EMBEDDING_SIZE: int = 384
    EMBEDDING_MODEL_DEVICE: str = "cpu"

    # OpenAI model
    OPENAI_MODEL_ID: str = 'gpt-4-1106-preview'

    # MongoDB configs
    MONGO_DATABASE_HOST: str = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
    MONGO_DATABASE_NAME: str = "scrabble"

    # QdrantDB config
    QDRANT_DATABASE_HOST: str = 'localhost'
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_DATABASE_URL: str = 'http://localhost:6333'
    CLEANED_DATA_OUTPUT_COLLECTION_NAME: str = 'cleaned_posts'
    QDRANT_APIKEY: Optional[str] = None

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str = 'guest'
    RABBITMQ_DEFAULT_PASSWORD: str = 'guest'
    RABBITMQ_HOST: str = 'localhost'
    RABBITMQ_PORT: int = 5673


settings = AppSettings()
