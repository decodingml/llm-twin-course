import httpx

from config import settings
from models.clean import ArticleCleanedModel, PostCleanedModel, RepositoryCleanedModel
from utils.logging import get_logger


logger = get_logger(__name__)


class SuperlinkedClient:
    def __init__(self, base_url=settings.SUPERLINKED_SERVER_URL) -> None:
        self.base_url = base_url
        self.timeout = 600
        self.headers = {"Accept": "*/*", "Content-Type": "application/json"}

    def ingest_repository(self, data: RepositoryCleanedModel) -> None:
        url = f"{self.base_url}/api/v1/ingest/repository_schema"
        logger.info(f"Sending repository {data.id} to Superlinked at {url}")
        
        response = httpx.post(url, headers=self.headers, json=data.model_dump(), timeout=self.timeout)

        if response.status_code != 202:
            raise httpx.HTTPStatusError(
                "Ingestion failed", request=response.request, response=response
            )

    def ingest_post(self, data: PostCleanedModel) -> None:
        url = f"{self.base_url}/api/v1/ingest/post_schema"
        logger.info(f"Sending post {data.id} to Superlinked at {url}")
        
        response = httpx.post(url, headers=self.headers, json=data.model_dump(), timeout=self.timeout)

        if response.status_code != 202:
            raise httpx.HTTPStatusError(
                "Ingestion failed", request=response.request, response=response
            )

    def ingest_article(self, data: ArticleCleanedModel) -> None:
        url = f"{self.base_url}/api/v1/ingest/article_schema"
        logger.info(f"Sending article {data.id} to Superlinked at {url}")
        
        response = httpx.post(url, headers=self.headers, json=data.model_dump(), timeout=self.timeout)

        if response.status_code != 202:
            raise httpx.HTTPStatusError(
                "Ingestion failed", request=response.request, response=response
            )

    def search_repository(
        self, search_query: str, platform: str, limit: int
    ) -> list[RepositoryCleanedModel]:
        url = f"{self.base_url}/api/v1/search/repository_query"
        
        data = {"search_query": search_query, "platform": platform, "limit": limit}
        response = httpx.post(url, headers=self.headers, json=data, timeout=self.timeout)

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                "Search failed", request=response.request, response=response
            )

        parsed_results = []
        for result in response.json()["results"]:
            parsed_results.append(RepositoryCleanedModel(**result["obj"]))

        return parsed_results

    def search_post(
        self, search_query: str, platform: str, limit: int
    ) -> list[PostCleanedModel]:
        url = f"{self.base_url}/api/v1/search/post_query"
        data = {"search_query": search_query, "platform": platform, "limit": limit}
        response = httpx.post(url, headers=self.headers, json=data, timeout=self.timeout)

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                "Search failed", request=response.request, response=response
            )

        parsed_results = []
        for result in response.json()["results"]:
            parsed_results.append(PostCleanedModel(**result["obj"]))

        return parsed_results

    def search_article(
        self, search_query: str, platform: str, limit: int
    ) -> list[ArticleCleanedModel]:
        url = f"{self.base_url}/api/v1/search/article_query"
        data = {"search_query": search_query, "platform": platform, "limit": limit}
        response = httpx.post(url, headers=self.headers, json=data, timeout=self.timeout)

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                "Search failed", request=response.request, response=response
            )

        parsed_results = []
        for result in response.json()["results"]:
            parsed_results.append(ArticleCleanedModel(**result["obj"]))

        return parsed_results
