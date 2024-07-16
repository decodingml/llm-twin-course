from bytewax.outputs import DynamicSink, StatelessSinkPartition
from models.clean import CleanedModel
from superlinked_client import SuperlinkedClient
from tqdm import tqdm
from utils.logging import get_logger

logger = get_logger(__name__)


class SuperlinkedOutputSink(DynamicSink):
    def __init__(self, client: SuperlinkedClient) -> None:
        self._client = client

    def build(self, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        return SuperlinkedSinkPartition(client=self._client)


class SuperlinkedSinkPartition(StatelessSinkPartition):
    def __init__(self, client: SuperlinkedClient):
        self._client = client

    def write_batch(self, items: list[CleanedModel]) -> None:
        for item in tqdm(items, desc="Sending items to Superlinked..."):
            match item.type:
                case "repositories":
                    self._client.ingest_repository(item)
                case "posts":
                    self._client.ingest_post(item)
                case "articles":
                    self._client.ingest_article(item)
                case _:
                    logger.error(f"Unknown item type: {item.type}")
