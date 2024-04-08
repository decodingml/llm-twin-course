from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from streaming_pipeline.settings import settings


class MongoDatabaseConnector:

    _instance: MongoClient = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.MONGO_DATABASE_HOST)
            except ConnectionFailure as e:
                print(f"Couldn't connect to the database: {str(e)}")
                raise

        print(f"Connection to database with uri: {settings.MONGO_DATABASE_HOST} successful")
        return cls._instance

    def get_database(self):
        return self._instance[settings.MONGO_DATABASE_NAME]

    def close(self):
        if self._instance:
            self._instance.close()
            print("Connected to database has been closed.")


connection = MongoDatabaseConnector()
