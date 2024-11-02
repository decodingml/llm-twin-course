from pydantic_settings import BaseSettings
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
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.text_similarity_space import (
    TextSimilaritySpace,
    chunk,
)
from superlinked.framework.dsl.storage.redis_vector_database import RedisVectorDatabase


class Settings(BaseSettings):
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-mpnet-base-v2"

    REDIS_HOSTNAME: str = "redis"
    REDIS_PORT: int = 6379


settings = Settings()


# ----------------- SCHEMAS ----------------- #


@schema
class PostSchema:
    id: IdField
    platform: String
    content: String
    author_id: String
    type: String


@schema
class ArticleSchema:
    id: IdField
    platform: String
    link: String
    content: String
    author_id: String
    type: String


@schema
class RepositorySchema:
    id: IdField
    platform: String
    name: String
    link: String
    content: String
    author_id: String
    type: String


post = PostSchema()
article = ArticleSchema()
repository = RepositorySchema()

# ----------------- SPACES ----------------- #


articles_space_content = TextSimilaritySpace(
    text=chunk(article.content, chunk_size=500, chunk_overlap=50),
    model=settings.EMBEDDING_MODEL_ID,
)
articles_space_plaform = CategoricalSimilaritySpace(
    category_input=article.platform,
    categories=["medium", "superlinked"],
    negative_filter=-5.0,
)

repository_space_content = TextSimilaritySpace(
    text=chunk(repository.content, chunk_size=1000, chunk_overlap=50),
    model=settings.EMBEDDING_MODEL_ID,
)
repository_space_plaform = CategoricalSimilaritySpace(
    category_input=repository.platform,
    categories=["github", "gitlab"],
    negative_filter=-5.0,
)

post_space_content = TextSimilaritySpace(
    text=chunk(post.content, chunk_size=300, chunk_overlap=50),
    model=settings.EMBEDDING_MODEL_ID,
)
post_space_plaform = CategoricalSimilaritySpace(
    category_input=post.platform,
    categories=["linkedin", "twitter"],
    negative_filter=-5.0,
)


# ----------------- INDEXES ----------------- #

article_index = Index(
    [articles_space_content, articles_space_plaform],
    fields=[article.author_id],
)
repository_index = Index(
    [repository_space_content, repository_space_plaform],
    fields=[repository.author_id],
)
post_index = Index(
    [post_space_content, post_space_plaform],
    fields=[post.author_id],
)

# ----------------- QUERIES ----------------- #

post_query = (
    Query(
        post_index,
        weights={
            post_space_content: Param("content_weight"),
            post_space_plaform: Param("platform_weight"),
        },
    )
    .find(post)
    .similar(post_space_content.text, Param("search_query"))
    .similar(post_space_plaform.category, Param("platform"))
    .filter(post.author_id == Param("author_id"))
    .limit(Param("limit"))
)
article_query = (
    Query(
        article_index,
        weights={
            articles_space_content: Param("content_weight"),
            articles_space_plaform: Param("platform_weight"),
        },
    )
    .find(article)
    .similar(articles_space_content.text, Param("search_query"))
    .similar(articles_space_plaform.category, Param("platform"))
    .filter(article.author_id == Param("author_id"))
    .limit(Param("limit"))
)
repository_query = (
    Query(
        repository_index,
        weights={
            repository_space_content: Param("content_weight"),
            repository_space_plaform: Param("platform_weight"),
        },
    )
    .find(repository)
    .similar(repository_space_content.text, Param("search_query"))
    .similar(repository_space_plaform.category, Param("platform"))
    .filter(repository.author_id == Param("author_id"))
    .limit(Param("limit"))
)

# ----------------- SOURCES ----------------- #

article_source = RestSource(article)
repository_source = RestSource(repository)
post_source = RestSource(post)


# ----------------- VECTOR DB ----------------- #

vector_database = RedisVectorDatabase(
    settings.REDIS_HOSTNAME,  # (Mandatory) This is your redis URL without any port or extra fields
    settings.REDIS_PORT,  # (Mandatory) This is the port and it should be an integer
)


# ----------------- EXECUTOR ----------------- #

executor = RestExecutor(
    sources=[article_source, repository_source, post_source],
    indices=[article_index, repository_index, post_index],
    queries=[
        RestQuery(RestDescriptor("article_query"), article_query),
        RestQuery(RestDescriptor("repository_query"), repository_query),
        RestQuery(RestDescriptor("post_query"), post_query),
    ],
    vector_database=vector_database,
)
SuperlinkedRegistry.register(executor)
