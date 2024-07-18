from datetime import datetime, timedelta, timezone

from superlinked.framework.common.dag.context import CONTEXT_COMMON, CONTEXT_COMMON_NOW
from superlinked.framework.common.dag.period_time import PeriodTime
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import Integer, String, StringList, Timestamp
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.data_loader_source import DataFormat, DataLoaderConfig, DataLoaderSource
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.number_space import Mode, NumberSpace
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase

START_OF_2024_TS = int(datetime(2024, 1, 2, tzinfo=timezone.utc).timestamp())
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: START_OF_2024_TS}}


@schema
class Review:
    rating: Integer
    timestamp: Timestamp
    verified_purchase: StringList
    review_text: String
    id: IdField


review = Review()


rating_space = NumberSpace(review.rating, min_value=1, max_value=5, mode=Mode.MAXIMUM)
recency_space = RecencySpace(review.timestamp, period_time_list=PeriodTime(timedelta(days=3650)))
verified_category_space = CategoricalSimilaritySpace(
    review.verified_purchase,
    categories=["True", "False"],
    uncategorized_as_category=False,
    negative_filter=-5,
)
relevance_space = TextSimilaritySpace(review.review_text, model="sentence-transformers/all-mpnet-base-v2")

index = Index([relevance_space, recency_space, rating_space, verified_category_space])

source: RestSource = RestSource(review)


query = (
    Query(
        index,
        weights={
            rating_space: Param("rating_weight"),
            recency_space: Param("recency_weight"),
            verified_category_space: Param("verified_category_weight"),
            relevance_space: Param("relevance_weight"),
        },
    )
    .find(review)
    .similar(relevance_space.text, Param("query_text"))
    .similar(verified_category_space.category, Param("query_verified"))
)

config = DataLoaderConfig(
    "https://storage.googleapis.com/superlinked-preview-test-data/amazon_dataset_1000.jsonl",
    DataFormat.JSON,
    pandas_read_kwargs={"lines": True, "chunksize": 100},
)
loader_source: DataLoaderSource = DataLoaderSource(review, config)

executor = RestExecutor(
    sources=[source, loader_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
    context_data=EXECUTOR_DATA,
)

SuperlinkedRegistry.register(executor)
