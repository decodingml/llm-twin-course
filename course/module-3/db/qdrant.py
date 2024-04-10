from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Batch, Distance, VectorParams

from settings import settings


class QdrantDatabaseConnector:
    _instance: QdrantClient = None

    def __init__(self):

        if self._instance is None:
            try:
                self._instance = QdrantClient(host=settings.QDRANT_DATABASE_HOST, port=settings.QDRANT_DATABASE_PORT)
            except UnexpectedResponse as e:
                print(f"Couldn't connect to the database: {str(e)}")
                raise

    def get_collection(self, collection_name: str):
        return self._instance.get_collection(collection_name=collection_name)

    def create_non_vector_collection(self, collection_name: str):
        print(f"Created collection: {collection_name}")
        self._instance.create_collection(collection_name=collection_name, vectors_config={})

    def create_vector_collection(self, collection_name: str):
        self._instance.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=settings.EMBEDDING_SIZE, distance=Distance.COSINE),
        )

    def write_data(self, collection_name: str, points: Batch):
        try:
            self._instance.upsert(collection_name=collection_name, points=points)
            print(f"Successfully inserted {len(points.ids)} point(s) into {collection_name}.")
        except Exception as e:
            print(f"An error occurred while inserting data: {str(e)}")
            raise

    def close(self):
        if self._instance:
            self._instance.close()
            print("Connected to database has been closed.")


connection = QdrantDatabaseConnector()
