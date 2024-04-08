from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client.http.api_client import UnexpectedResponse
from qdrant_client.models import Batch

from db.qdrant import QdrantDatabaseConnector
from models.base import DBDataModel


class QdrantOutput(DynamicSink):
    """
    Class that facilitates the connection between and Qdrant Vector DB
    Inherits DynamicSink because of the ability to create different sink sources (e.g, vector and non-vector collections)
    """

    def __init__(self, connection: QdrantDatabaseConnector, sink_type: str):
        self._connection = connection
        self._sink_type = sink_type

        try:
            self._connection.get_collection(collection_name="cleaned_posts")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_non_vector_collection(collection_name="cleaned_posts")

        try:
            self._connection.get_collection(collection_name="cleaned_articles")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_non_vector_collection(collection_name="cleaned_articles")

        try:
            self._connection.get_collection(collection_name="cleaned_repositories")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_non_vector_collection(collection_name="cleaned_repositories")

        try:
            self._connection.get_collection(collection_name="vector_posts")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_vector_collection(collection_name="vector_posts")

        try:
            self._connection.get_collection(collection_name="vector_articles")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_vector_collection(collection_name="vector_articles")

        try:
            self._connection.get_collection(collection_name="vector_repositories")
        except UnexpectedResponse as e:
            print(f"Error when accessing the collection: {e}")
            self._connection.create_vector_collection(collection_name="vector_repositories")

    def build(self, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        if self._sink_type == "clean":
            return QdrantCleanedDataSink(connection=self._connection)
        elif self._sink_type == "vector":
            return QdrantVectorDataSink(connection=self._connection)


class QdrantCleanedDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[DBDataModel]) -> None:
        payloads = [item.save() for item in items]
        ids, data = zip(*payloads)
        collection_name = dispatch_clean_collection(data_type=data[0]["type"])
        self._client.write_data(collection_name=collection_name, points=Batch(ids=ids, vectors={}, payloads=data))


class QdrantVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[DBDataModel]) -> None:
        payloads = [item.save() for item in items]
        ids, vectors, meta_data = zip(*payloads)
        collection_name = dispatch_vector_collection(data_type=meta_data[0]["type"])
        self._client.write_data(
            collection_name=collection_name, points=Batch(ids=ids, vectors=vectors, payloads=meta_data)
        )


def dispatch_clean_collection(data_type: str) -> str:
    if data_type == "posts":
        return "cleaned_posts"
    elif data_type == "articles":
        return "cleaned_articles"
    elif data_type == "repositories":
        return "cleaned_repositories"


def dispatch_vector_collection(data_type: str) -> str:
    if data_type == "posts":
        return "vector_posts"
    elif data_type == "articles":
        return "vector_articles"
    elif data_type == "repositories":
        return "vector_repositories"
