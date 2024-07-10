from datetime import datetime

import utils
from models import utils as model_utils
from models.clean import (ArticleCleanedModel, PostCleanedModel,
                          RepositoryCleanedModel)
from models.schemas import article, post, repository
from superlinked.framework.common.dag.context import (CONTEXT_COMMON,
                                                      CONTEXT_COMMON_NOW)
from superlinked.framework.common.parser.dataframe_parser import \
    DataFrameParser
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import \
    InMemoryExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.space.text_similarity_space import (
    TextSimilaritySpace, chunk
)

from superlinked_engine import SuperlinkedEngine


START_OF_2024_TS = int(datetime(2024, 1, 2).timestamp())
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: START_OF_2024_TS}}

mock_data_articles = [
    ArticleCleanedModel(id="1", platform="Twitter", link="http://twitter.com/1", cleaned_content="Cleaned content 1", author_id="author_1", type="social"),
    ArticleCleanedModel(id="2", platform="Facebook", link="http://facebook.com/2", cleaned_content="Cleaned content 2", author_id="author_2", type="social"),
    ArticleCleanedModel(id="3", platform="LinkedIn", link="http://linkedin.com/3", cleaned_content="Cleaned content 3", author_id="author_3", type="professional"),
    ArticleCleanedModel(id="4", platform="Medium", link="http://medium.com/4", cleaned_content="Cleaned content 4", author_id="author_4", type="blog"),
    ArticleCleanedModel(id="5", platform="Reddit", link="http://reddit.com/5", cleaned_content="Cleaned content 5", author_id="author_5", type="forum")
]
articles_df = model_utils.pydantic_models_to_dataframe(mock_data_articles)

mock_data_posts = [
    PostCleanedModel(id="1", platform="Twitter", cleaned_content="Cleaned content 1", author_id="author_1", type="social"),
    PostCleanedModel(id="2", platform="Facebook", cleaned_content="Cleaned content 2", author_id="author_2", type="social"),
    PostCleanedModel(id="3", platform="LinkedIn", cleaned_content="Cleaned content 3", author_id="author_3", type="professional"),
    PostCleanedModel(id="4", platform="Medium", cleaned_content="Cleaned content 4", author_id="author_4", type="blog"),
    PostCleanedModel(id="5", platform="Reddit", cleaned_content="Cleaned content 5", author_id="author_5", type="forum")
]
posts_df = model_utils.pydantic_models_to_dataframe(mock_data_posts)

mock_data_repositories = [
    RepositoryCleanedModel(id="1", name="Repo1", link="http://github.com/repo1", cleaned_content="Cleaned content repo 1", owner_id="owner_1", type="public"),
    RepositoryCleanedModel(id="2", name="Repo2", link="http://gitlab.com/repo2", cleaned_content="Cleaned content repo 2", owner_id="owner_2", type="private"),
    RepositoryCleanedModel(id="3", name="Repo3", link="http://bitbucket.com/repo3", cleaned_content="Cleaned content repo 3", owner_id="owner_3", type="public"),
    RepositoryCleanedModel(id="4", name="Repo4", link="http://github.com/repo4", cleaned_content="Cleaned content repo 4", owner_id="owner_4", type="public"),
    RepositoryCleanedModel(id="5", name="Repo5", link="http://gitlab.com/repo5", cleaned_content="Cleaned content repo 5", owner_id="owner_5", type="private")
]
repositories_df = model_utils.pydantic_models_to_dataframe(mock_data_repositories)

if __name__ == "__main__":
    print("Running using engine!")
    
    engine = SuperlinkedEngine()
    engine.put(articles_df, data_type="articles")
    engine.put(posts_df, data_type="posts")
    engine.put(repositories_df, data_type="repositories")
    
    print("Articles:")
    article_results = engine.query("Cleaned content 1", data_type="articles")
    print(article_results)
    print("-" * 100)
    
    print("Posts:")
    post_results = engine.query("Cleaned content 1", data_type="posts")
    print(post_results)
    print("-" * 100)
    


if __name__ == "__main___":
    articles_space = TextSimilaritySpace(
        text=chunk(article.cleaned_content, chunk_size=500, chunk_overlap=20),
        model="sentence-transformers/all-mpnet-base-v2",
    )
    repository_space = TextSimilaritySpace(
        text=chunk(repository.cleaned_content, chunk_size=500, chunk_overlap=20),
        model="sentence-transformers/all-mpnet-base-v2",
    )
    post_space = TextSimilaritySpace(
        text=chunk(post.cleaned_content, chunk_size=500, chunk_overlap=20),
        model="sentence-transformers/all-mpnet-base-v2",
    )
    article_index = Index([articles_space])
    repository_index = Index([repository_space])
    post_index = Index([post_space])
    
    article_parser = DataFrameParser(article, mapping={article.id: "index"})
    repository_parser = DataFrameParser(repository, mapping={repository.id: "index"})
    post_parser = DataFrameParser(post, mapping={post.id: "index"})
    
    article_source: InMemorySource = InMemorySource(article, parser=article_parser)
    repository_source: InMemorySource = InMemorySource(repository, parser=repository_parser)
    post_source: InMemorySource = InMemorySource(post, parser=post_parser)
    
    executor = InMemoryExecutor(
        sources=[article_source, repository_source, post_source], indices=[article_index, repository_index, post_index], context_data=EXECUTOR_DATA
    )
    app = executor.run()
    
    article_source.put([articles_df])
    post_source.put([posts_df])
    repository_source.put([repositories_df])
    
    article_query = (
        Query(
            article_index,
            weights={
                articles_space: Param("relevance_weight"),
            },
        )
        .find(article)
        .similar(articles_space.text, Param("search_query"))
        .limit(Param("limit"))
    )
    article_results = app.query(
        article_query,
        relevance_weight=1,
        search_query="Cleaned content 1",
        limit=3,
    )
    print("Articles:")
    print(utils.present_result(article_results))
    
    print("-" * 100)
    
    post_query = (
        Query(
            post_index,
            weights={
                post_space: Param("relevance_weight"),
            },
        )
        .find(post)
        .similar(post_space.text, Param("search_query"))
        .limit(Param("limit"))
    )
    post_results = app.query(
        post_query,
        relevance_weight=1,
        search_query="Cleaned content 1",
        limit=3,
    )
    print("Posts:")
    print(utils.present_result(post_results))
