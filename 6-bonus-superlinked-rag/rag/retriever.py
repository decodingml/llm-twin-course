import concurrent.futures

import utils
from models.documents import Document
from rag.query_expanison import QueryExpansion
from rag.reranking import Reranker
from rag.self_query import SelfQuery
from superlinked_client import SuperlinkedClient
from utils.logging import get_logger

logger = get_logger(__name__)


class VectorRetriever:
    """
    Class for retrieving vectors from a Vector store in a RAG system using query expansion and Multitenancy search.
    """

    def __init__(self, query: str) -> None:
        self._client = SuperlinkedClient()
        self.query = query
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(
        self, generated_query: str, author_id: str, k: int
    ) -> list[Document]:
        assert k > 3, "k should be greater than 3"

        posts = self._client.search_post(
            search_query=generated_query,
            platform="linkedin",
            author_id=author_id,
            limit=k // 3,
        )
        logger.info("Successfully retrieved posts.", num_posts=len(posts))
        logger.info("Total posts content length.", total_content_len=sum([len(post.content) for post in posts]))
        
        articles = self._client.search_article(
            search_query=generated_query,
            platform="medium",
            author_id=author_id,
            limit=k // 3,
        )
        logger.info("Successfully retrieved articles.", num_articles=len(articles))
        logger.info("Total articles content length.", total_content_len=sum([len(article.content) for article in articles]))
        
        repositories = self._client.search_repository(
            search_query=generated_query,
            platform="github",
            author_id=author_id,
            limit=k // 3,
        )
        logger.info("Successfully retrieved repositories.", num_repositories=len(repositories))
        logger.info("Total repositories content length.", total_content_len=sum([len(repository.content) for repository in repositories]))

        return posts + articles + repositories

    def retrieve_top_k(self, k: int, to_expand_to_n_queries: int) -> list:
        generated_queries = self._query_expander.generate_response(
            self.query, to_expand_to_n=to_expand_to_n_queries
        )
        logger.info(
            "Successfully generated queries for search.",
            num_queries=len(generated_queries),
        )

        author_id = self._metadata_extractor.generate_response(self.query)
        if author_id:
            logger.info(
                "Successfully extracted the author_id from the query.",
                author_id=author_id,
            )
        else:
            logger.info("Couldn't extract the author_id from the query. Defaulting to empty string.")
            author_id  = ""

        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, author_id, k)
                for query in generated_queries
            ]

            documents = [
                task.result() for task in concurrent.futures.as_completed(search_tasks)
            ]
            documents = utils.flatten(documents)

        logger.info("All documents retrieved successfully.", num_documents=len(documents))

        return documents

    def rerank(self, documents: list[Document], keep_top_k: int) -> list[str]:
        content_list = [document.content for document in documents]
        rerank_documents = self._reranker.generate_response(
            query=self.query, passages=content_list, keep_top_k=keep_top_k
        )

        logger.info("Documents reranked successfully.", num_documents=len(rerank_documents))

        return rerank_documents

    def set_query(self, query: str) -> None:
        self.query = query
