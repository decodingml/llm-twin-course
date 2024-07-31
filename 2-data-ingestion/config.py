from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB configs
    MONGO_DATABASE_HOST: str = (
        "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"
    )
    MONGO_DATABASE_NAME: str = "scrabble"

    RABBITMQ_HOST: str = "mq"  # or localhost if running outside Docker
    RABBITMQ_PORT: int = 5672
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_QUEUE_NAME: str = "default"


settings = Settings()
