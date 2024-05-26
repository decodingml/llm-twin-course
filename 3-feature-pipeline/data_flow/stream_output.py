import logger_utils
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from db.qdrant import QdrantDatabaseConnector
from models.base import VectorDBDataModel
from qdrant_client.http.api_client import UnexpectedResponse
from qdrant_client.models import Batch

logger = logger_utils.get_logger(__name__)


class QdrantOutput(DynamicSink):
    """
    Bytewax class that facilitates the connection to a Qdrant vector DB.
    Inherits DynamicSink because of the ability to create different sink sources (e.g, vector and non-vector collections)
    """

    def __init__(self, connection: QdrantDatabaseConnector, sink_type: str):
        self._connection = connection
        self._sink_type = sink_type

        try:
            self._connection.get_collection(collection_name="cleaned_posts")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="cleaned_posts",
            )

            self._connection.create_non_vector_collection(
                collection_name="cleaned_posts"
            )

        try:
            self._connection.get_collection(collection_name="cleaned_articles")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="cleaned_articles",
            )

            self._connection.create_non_vector_collection(
                collection_name="cleaned_articles"
            )

        try:
            self._connection.get_collection(collection_name="cleaned_repositories")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="cleaned_repositories",
            )

            self._connection.create_non_vector_collection(
                collection_name="cleaned_repositories"
            )

        try:
            self._connection.get_collection(collection_name="vector_posts")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="vector_posts",
            )

            self._connection.create_vector_collection(collection_name="vector_posts")

        try:
            self._connection.get_collection(collection_name="vector_articles")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="vector_articles",
            )

            self._connection.create_vector_collection(collection_name="vector_articles")

        try:
            self._connection.get_collection(collection_name="vector_repositories")
        except UnexpectedResponse:
            logger.info(
                "Couldn't access the collection. Creating a new one...",
                collection_name="vector_repositories",
            )

            self._connection.create_vector_collection(
                collection_name="vector_repositories"
            )

    def build(self, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        if self._sink_type == "clean":
            return QdrantCleanedDataSink(connection=self._connection)
        elif self._sink_type == "vector":
            return QdrantVectorDataSink(connection=self._connection)
        else:
            raise ValueError(f"Unsupported sink type: {self._sink_type}")


class QdrantCleanedDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, data = zip(*payloads)
        collection_name = get_clean_collection(data_type=data[0]["type"])
        self._client.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors={}, payloads=data),
        )

        logger.info(
            "Successfully inserted requested cleaned point(s)",
            collection_name=collection_name,
            num=len(ids),
        )


class QdrantVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, vectors, meta_data = zip(*payloads)
        collection_name = get_vector_collection(data_type=meta_data[0]["type"])
        self._client.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors=vectors, payloads=meta_data),
        )

        logger.info(
            "Successfully inserted requested vector point(s)",
            collection_name=collection_name,
            num=len(ids),
        )


def get_clean_collection(data_type: str) -> str:
    if data_type == "posts":
        return "cleaned_posts"
    elif data_type == "articles":
        return "cleaned_articles"
    elif data_type == "repositories":
        return "cleaned_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")


def get_vector_collection(data_type: str) -> str:
    if data_type == "posts":
        return "vector_posts"
    elif data_type == "articles":
        return "vector_articles"
    elif data_type == "repositories":
        return "vector_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
