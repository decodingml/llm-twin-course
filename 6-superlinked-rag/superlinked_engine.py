from datetime import datetime
from functools import cached_property

from models.schemas import article, post, repository
from pandas import DataFrame
from singleton import SingletonMeta
from superlinked.framework.common.dag.context import CONTEXT_COMMON, CONTEXT_COMMON_NOW
from superlinked.framework.common.parser.dataframe_parser import DataFrameParser
from superlinked.framework.dsl.executor.in_memory.in_memory_executor import (
    InMemoryExecutor,
)
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query, QueryObj
from superlinked.framework.dsl.source.in_memory_source import InMemorySource
from superlinked.framework.dsl.space.text_similarity_space import (
    TextSimilaritySpace,
    chunk,
)


class SuperlinkedEngine(metaclass=SingletonMeta):
    EXECUTOR_DATA = {
        CONTEXT_COMMON: {CONTEXT_COMMON_NOW: int(datetime(2024, 1, 2).timestamp())}
    }

    def __init__(self) -> None:
        self.articles_space = TextSimilaritySpace(
            text=chunk(article.cleaned_content, chunk_size=500, chunk_overlap=20),
            model="sentence-transformers/all-mpnet-base-v2",
        )
        self.repository_space = TextSimilaritySpace(
            text=chunk(repository.cleaned_content, chunk_size=500, chunk_overlap=20),
            model="sentence-transformers/all-mpnet-base-v2",
        )
        self.post_space = TextSimilaritySpace(
            text=chunk(post.cleaned_content, chunk_size=500, chunk_overlap=20),
            model="sentence-transformers/all-mpnet-base-v2",
        )

        self.article_index = Index([self.articles_space])
        self.repository_index = Index([self.repository_space])
        self.post_index = Index([self.post_space])

        self.article_parser = DataFrameParser(article, mapping={article.id: "index"})
        self.repository_parser = DataFrameParser(
            repository, mapping={repository.id: "index"}
        )
        self.post_parser = DataFrameParser(post, mapping={post.id: "index"})

        self.article_source: InMemorySource = InMemorySource(
            article, parser=self.article_parser
        )
        self.repository_source: InMemorySource = InMemorySource(
            repository, parser=self.repository_parser
        )
        self.post_source: InMemorySource = InMemorySource(post, parser=self.post_parser)

        self.executor = InMemoryExecutor(
            sources=[self.article_source, self.repository_source, self.post_source],
            indices=[self.article_index, self.repository_index, self.post_index],
            context_data=self.EXECUTOR_DATA,
        )
        self.app = self.executor.run()
        
    @cached_property
    def post_query(self) -> QueryObj:
        return (
            Query(
                self.post_index,
                weights={
                    self.post_space: Param("relevance_weight"),
                },
            )
            .find(post)
            .similar(self.post_space.text, Param("search_query"))
            .limit(Param("limit"))
        )

    @cached_property
    def article_query(self) -> QueryObj:
        return (
            Query(
                self.article_index,
                weights={
                    self.articles_space: Param("relevance_weight"),
                },
            )
            .find(article)
            .similar(self.articles_space.text, Param("search_query"))
            .limit(Param("limit"))
        )
        
    @cached_property
    def repository_query(self) -> QueryObj:
        return (
            Query(
                self.repository_index,
                weights={
                    self.repository_space: Param("relevance_weight"),
                },
            )
            .find(repository)
            .similar(self.repository_space.text, Param("search_query"))
            .limit(Param("limit"))
        )

    def put(self, df: DataFrame, *, data_type: str) -> None:
        if data_type == "posts":
            self.post_source.put([df])
        elif data_type == "articles":
            self.article_source.put([df])
        elif data_type == "repositories":
            self.repository_source.put([df])
        else:
            raise RuntimeError(f"Unsupported data type: {data_type}")

    def query(self, text: str, *, data_type: str) -> DataFrame:
        query_kwargs = {
            "relevant_weight": 1,
            "search_query": text,
            "limit": 3
        }
        if data_type == "posts":
            query_kwargs["query_obj"] = self.post_query
        elif data_type == "articles":
            query_kwargs["query_obj"] = self.article_query
        elif data_type == "repositories":
            query_kwargs["query_obj"] = self.repository_query
        else:
            raise RuntimeError(f"Unsupported data type: {data_type}")
        
        result = self.app.query(**query_kwargs)

        return result.to_pandas()
