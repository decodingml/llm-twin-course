from datetime import datetime

from superlinked.framework.common.dag.context import CONTEXT_COMMON, CONTEXT_COMMON_NOW
from superlinked.framework.common.parser.dataframe_parser import DataFrameParser
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryExecutor,
)
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.space.text_similarity_space import (
    TextSimilaritySpace,
    chunk,
)

import utils

from models.clean import ArticleCleanedModel
from models.clean_schemas import article
from models import utils as model_utils

START_OF_2024_TS = int(datetime(2024, 1, 2).timestamp())
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: START_OF_2024_TS}}

mock_data = [
    ArticleCleanedModel(id="1", platform="Twitter", link="http://twitter.com/1", cleaned_content="Cleaned content 1", author_id="author_1", type="social"),
    ArticleCleanedModel(id="2", platform="Facebook", link="http://facebook.com/2", cleaned_content="Cleaned content 2", author_id="author_2", type="social"),
    ArticleCleanedModel(id="3", platform="LinkedIn", link="http://linkedin.com/3", cleaned_content="Cleaned content 3", author_id="author_3", type="professional"),
    ArticleCleanedModel(id="4", platform="Medium", link="http://medium.com/4", cleaned_content="Cleaned content 4", author_id="author_4", type="blog"),
    ArticleCleanedModel(id="5", platform="Reddit", link="http://reddit.com/5", cleaned_content="Cleaned content 5", author_id="author_5", type="forum")
]
articles_df = model_utils.pydantic_models_to_dataframe(mock_data)


if __name__ == "__main__":
    relevance_space = TextSimilaritySpace(
        text=chunk(article.cleaned_content, chunk_size=500, chunk_overlap=20),
        model="sentence-transformers/all-mpnet-base-v2",
    )

    article_index = Index([relevance_space])
    article_parser = DataFrameParser(article, mapping={article.id: "index"})
    source: InMemorySource = InMemorySource(article, parser=article_parser)
    executor = InMemoryExecutor(
        sources=[source], indices=[article_index], context_data=EXECUTOR_DATA
    )
    app = executor.run()
    source.put([articles_df])
    
    # our simple query will make a search term possible, and gives us the opportunity to weight input aspects (relevance and recency against each other)
    knowledgebase_query = (
        Query(
            article_index,
            weights={
                relevance_space: Param("relevance_weight"),
            },
        )
        .find(article)
        .similar(relevance_space.text, Param("search_query"))
        .limit(Param("limit"))
    )
    
    only_relevance_result = app.query(
        knowledgebase_query,
        relevance_weight=1,
        recency_weight=0,
        search_query="What should management monitor?",
        limit=10,
    )
    print(utils.present_result(only_relevance_result))
