import logger_utils
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from settings import settings

logger = logger_utils.get_logger(__name__)


class MongoDatabaseConnector:
    _instance: MongoClient = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.MONGO_DATABASE_HOST)
            except ConnectionFailure:
                logger.exception(
                    "Couldn't connect to the database",
                    database_host=settings.MONGO_DATABASE_HOST,
                )

                raise

        logger.info(
            "Connection to database successful", uri=settings.MONGO_DATABASE_HOST
        )
        return cls._instance

    def get_database(self):
        return self._instance[settings.MONGO_DATABASE_NAME]

    def close(self):
        if self._instance:
            self._instance.close()
            logger.info(
                "Connected to database has been closed.",
                uri=settings.MONGO_DATABASE_HOST,
            )


connection = MongoDatabaseConnector()
