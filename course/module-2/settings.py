from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):

    # MongoDB configs
    MONGO_DATABASE_HOST: str = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
    MONGO_DATABASE_NAME: str = "scrabble"


settings = AppSettings()
