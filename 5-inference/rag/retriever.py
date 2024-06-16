import concurrent.futures

import core.logger_utils as logger_utils
from core.db.qdrant import QdrantDatabaseConnector
from qdrant_client import models
from sentence_transformers.SentenceTransformer import SentenceTransformer

import utils
from rag.query_expanison import QueryExpansion
from rag.reranking import Reranker
from rag.self_query import SelfQuery
from settings import settings

logger = logger_utils.get_logger(__name__)


class VectorRetriever:
    """
    Class for retrieving vectors from a Vector store in a RAG system using query expansion and Multitenancy search.
    """

    def __init__(self, query: str) -> None:
        self._client = QdrantDatabaseConnector()
        self.query = query
        self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(
        self, generated_query: str, metadata_filter_value: str, k: int
    ):
        assert k > 3, "k should be greater than 3"

        query_vector = self._embedder.encode(generated_query).tolist()

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
                query_vector=query_vector,
                limit=k // 3,
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
                query_vector=query_vector,
                limit=k // 3,
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
                query_vector=query_vector,
                limit=k // 3,
            ),
        ]

        return utils.flatten(vectors)

    def retrieve_top_k(self, k: int, to_expand_to_n_queries: int) -> list:
        generated_queries = self._query_expander.generate_response(
            self.query, to_expand_to_n=to_expand_to_n_queries
        )
        logger.info(
            "Successfully generated queries for search.",
            num_queries=len(generated_queries),
        )

        author_id = self._metadata_extractor.generate_response(self.query)
        logger.info(
            "Successfully extracted the author_id from the query.",
            author_id=author_id,
        )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, author_id, k)
                for query in generated_queries
            ]

            hits = [
                task.result() for task in concurrent.futures.as_completed(search_tasks)
            ]
            hits = utils.flatten(hits)

        logger.info("All documents retrieved successfully.", num_documents=len(hits))

        return hits

    def rerank(self, hits: list, keep_top_k: int) -> list[str]:
        content_list = [hit.payload["content"] for hit in hits]
        rerank_hits = self._reranker.generate_response(
            query=self.query, passages=content_list, keep_top_k=keep_top_k
        )

        logger.info("Documents reranked successfully.", num_documents=len(rerank_hits))

        return rerank_hits

    def set_query(self, query: str):
        self.query = query
