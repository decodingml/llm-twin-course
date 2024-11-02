from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.dsl.executor.rest.rest_configuration import RestQuery
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase


@schema
class YourSchema:
    id: IdField
    attribute: String


your_schema = YourSchema()

text_space = TextSimilaritySpace(text=your_schema.attribute, model="model-name")

index = Index(text_space)

query = (
    Query(index)
    .find(your_schema)
    .similar(
        text_space.text,
        Param("query_text"),
    )
)

your_source: RestSource = RestSource(your_schema)

executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
