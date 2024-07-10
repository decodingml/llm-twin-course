from bytewax.outputs import DynamicSink, StatelessSinkPartition

from models.clean import CleanedModel
from models.utils import group_by_type, pydantic_models_to_dataframe
from superlinked_engine import SuperlinkedEngine
from utils.logging import get_logger

logger = get_logger(__name__)


class SuperlinkedOutputSink(DynamicSink):
    def __init__(self, engine: SuperlinkedEngine) -> None:
        self._engine = engine

    def build(self, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        return SuperlinkedSinkPartition(engine=self._engine)


class SuperlinkedSinkPartition(StatelessSinkPartition):
    def __init__(self, engine: SuperlinkedEngine):
        self._engine = engine

    def write_batch(self, items: list[CleanedModel]) -> None:
        grouped_items = group_by_type(items)
        for item_type, scoped_items in grouped_items.items():
            scoped_items = pydantic_models_to_dataframe(scoped_items)
            try:
                self._engine.put(scoped_items, data_type=item_type)
            except Exception as e:
                logger.exception(
                    f"Failed to put items of type {item_type} into Superlinked."
                )
