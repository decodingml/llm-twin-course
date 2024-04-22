import concurrent.futures

from qdrant_client import QdrantClient, models
from rag.query_expanison import QueryExpansion
from rag.reranking import Reranker
from rag.self_query import SelfQuery
from sentence_transformers.SentenceTransformer import SentenceTransformer
from settings import settings


class VectorRetriever:
    """
    Class for retrieving vectors from a Vector store in a RAG system using query expansion and Multitenancy search.
    """

    def __init__(self, query: str):
        self._client = QdrantClient(
            host=settings.QDRANT_DATABASE_HOST, port=settings.QDRANT_DATABASE_PORT
        )
        self.query = query
        self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(
        self, generated_query: str, metadata_filter_value: str, k: int
    ):
        vectors = [
            self._client.search(
                collection_name="vector_posts",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(
                                value=metadata_filter_value,
                            ),
                        )
                    ]
                ),
                query_vector=self._embedder.encode(generated_query).tolist(),
                limit=k,
            ),
            self._client.search(
                collection_name="vector_articles",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(
                                value=metadata_filter_value,
                            ),
                        )
                    ]
                ),
                query_vector=self._embedder.encode(generated_query).tolist(),
                limit=k,
            ),
            self._client.search(
                collection_name="vector_repositories",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="owner_id",
                            match=models.MatchValue(
                                value=metadata_filter_value,
                            ),
                        )
                    ]
                ),
                query_vector=self._embedder.encode(generated_query).tolist(),
                limit=k,
            ),
        ]

        return vectors

    def retrieve_top_k(self, k: int) -> list:
        generated_queries = self._query_expander.generate_response(self.query)
        metadata_filter_value = self._metadata_extractor.generate_response(self.query)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(
                    self._search_single_query, query, metadata_filter_value, k
                )
                for query in generated_queries
            ]

            hits = [
                task.result() for task in concurrent.futures.as_completed(search_tasks)
            ]

            return hits

    def rerank(self, hits: list) -> list[str]:
        inner_list = hits[0][0]
        content_list = [hit.payload["content"] for hit in inner_list]
        passages = "\n".join(content_list)
        rerank_hits = self._reranker.generate_response(
            query=self.query, passages=passages
        )

        return rerank_hits

    def set_query(self, query: str):
        self.query = query
