from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB configs
    MONGO_DATABASE_HOST: str = "mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set"
    MONGO_DATABASE_NAME: str = "admin"

    RABBITMQ_HOST: str = "localhost"  # or the Docker host if running remotely
    RABBITMQ_PORT: int = 5673  # Port mapped in Docker Compose
    RABBITMQ_DEFAULT_USERNAME: str = "guest"  # Default username
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"  # Default password
    RABBITMQ_QUEUE_NAME: str = "default"


settings = Settings()
