from typing import TypeVar

import httpx

from config import settings
from models.documents import ArticleDocument, PostDocument, RepositoryDocument
from utils.logging import get_logger

logger = get_logger(__name__)


T = TypeVar("T", ArticleDocument, PostDocument, RepositoryDocument)


class SuperlinkedClient:
    def __init__(self, base_url=settings.SUPERLINKED_SERVER_URL) -> None:
        self.base_url = base_url
        self.timeout = 600
        self.headers = {"Accept": "*/*", "Content-Type": "application/json"}

        self._content_weight = 0.9
        self._platform_weight = 0.1

    def ingest_repository(self, data: RepositoryDocument) -> None:
        self.__ingest(f"{self.base_url}/api/v1/ingest/repository_schema", data)

    def ingest_post(self, data: PostDocument) -> None:
        self.__ingest(f"{self.base_url}/api/v1/ingest/post_schema", data)

    def ingest_article(self, data: ArticleDocument) -> None:
        self.__ingest(f"{self.base_url}/api/v1/ingest/article_schema", data)

    def __ingest(self, url: str, data: T) -> None:
        logger.info(f"Sending {type(data)} {data.id} to Superlinked at {url}")

        response = httpx.post(
            url, headers=self.headers, json=data.model_dump(), timeout=self.timeout
        )

        if response.status_code != 202:
            raise httpx.HTTPStatusError(
                "Ingestion failed", request=response.request, response=response
            )

        logger.info(f"Successfully sent {type(data)} {data.id} to Superlinked at {url}")

    def search_repository(
        self, search_query: str, platform: str, author_id: str, *, limit: int = 3
    ) -> list[RepositoryDocument]:
        return self.__search(
            f"{self.base_url}/api/v1/search/repository_query",
            RepositoryDocument,
            search_query,
            platform,
            author_id,
            limit=limit,
        )

    def search_post(
        self, search_query: str, platform: str, author_id: str, *, limit: int = 3
    ) -> list[PostDocument]:
        return self.__search(
            f"{self.base_url}/api/v1/search/post_query",
            PostDocument,
            search_query,
            platform,
            author_id,
            limit=limit,
        )

    def search_article(
        self, search_query: str, platform: str, author_id: str, *, limit: int = 3
    ) -> list[ArticleDocument]:
        return self.__search(
            f"{self.base_url}/api/v1/search/article_query",
            ArticleDocument,
            search_query,
            platform,
            author_id,
            limit=limit,
        )

    def __search(
        self,
        url: str,
        document_class: type[T],
        search_query: str,
        platform: str,
        author_id: str,
        *,
        limit: int = 3,
    ) -> list[T]:
        data = {
            "search_query": search_query,
            "platform": platform,
            "author_id": author_id,
            "limit": limit,
            "content_weight": self._content_weight,
            "platform_weight": self._platform_weight,
        }
        logger.info(f"Searching Superlinked for {document_class.__name__} at: {url}")
        response = httpx.post(
            url, headers=self.headers, json=data, timeout=self.timeout
        )

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                "Search failed", request=response.request, response=response
            )

        parsed_results = []
        for result in response.json()["results"]:
            parsed_results.append(document_class(**result["obj"]))

        logger.info(
            f"Successfully retrieved {len(parsed_results)} {document_class.__name__} from Superlinked for at: {url}"
        )

        return parsed_results
