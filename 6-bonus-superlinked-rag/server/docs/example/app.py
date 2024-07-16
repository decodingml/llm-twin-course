from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestQuery,
)
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
class CarSchema:
    id: IdField
    make: String
    model: String


car_schema = CarSchema()

car_make_text_space = TextSimilaritySpace(text=car_schema.make, model="all-MiniLM-L6-v2")
car_model_text_space = TextSimilaritySpace(text=car_schema.model, model="all-MiniLM-L6-v2")

index = Index([car_make_text_space, car_model_text_space])

query = (
    Query(index)
    .find(car_schema)
    .similar(car_make_text_space.text, Param("make"))
    .similar(car_model_text_space.text, Param("model"))
    .limit(Param("limit"))
)

car_source: RestSource = RestSource(car_schema)

executor = RestExecutor(
    sources=[car_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
