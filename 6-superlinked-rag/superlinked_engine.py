from datetime import datetime

from config import settings
from models.schemas import article, post, repository, schemas_repository
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
from superlinked.framework.dsl.space.categorical_similarity_space import (
    CategoricalSimilaritySpace,
)
from superlinked.framework.dsl.space.text_similarity_space import (
    TextSimilaritySpace,
    chunk,
)


class SuperlinkedEngine(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__build_spaces()
        self.__build_indices()
        self.__build_parses()
        self.__build_sources()
        self.__build_executor()
        
        self.app = self.executor.run()
        
    def __build_spaces(self) -> None:
        self.articles_space_content = TextSimilaritySpace(
            text=chunk(article.cleaned_content, chunk_size=500, chunk_overlap=50),
            model=settings.EMBEDDING_MODEL_ID,
        )
        self.articles_space_plaform = CategoricalSimilaritySpace(
            category_input=article.platform,
            categories=["medium", "superlinked"],
            negative_filter=-5.0,
        )

        self.repository_space_content = TextSimilaritySpace(
            text=chunk(repository.cleaned_content, chunk_size=600, chunk_overlap=50),
            model=settings.EMBEDDING_MODEL_ID,
        )
        self.repository_space_plaform = CategoricalSimilaritySpace(
            category_input=repository.platform,
            categories=["github", "gitlab"],
            negative_filter=-5.0,
        )

        self.post_space_content = TextSimilaritySpace(
            text=chunk(post.cleaned_content, chunk_size=300, chunk_overlap=50),
            model=settings.EMBEDDING_MODEL_ID,
        )
        self.post_space_plaform = CategoricalSimilaritySpace(
            category_input=post.platform,
            categories=["linkedin", "twitter"],
            negative_filter=-5.0,
        )
        
    def __build_indices(self) -> None:
        self.article_index = Index(
            [self.articles_space_content, self.articles_space_plaform],
            fields=[article.author_id],
        )
        self.repository_index = Index(
            [self.repository_space_content, self.repository_space_plaform],
            fields=[repository.author_id],
        )
        self.post_index = Index(
            [self.post_space_content, self.post_space_plaform],
            fields=[post.author_id],
            )
        
    def __build_parses(self) -> None:
        self.article_parser = DataFrameParser(article, mapping={article.id: "index"})
        self.repository_parser = DataFrameParser(
            repository, mapping={repository.id: "index"}
        )
        self.post_parser = DataFrameParser(post, mapping={post.id: "index"})
        
    def __build_sources(self) -> None:
         self.article_source: InMemorySource = InMemorySource(
            article, parser=self.article_parser
        )
         self.repository_source: InMemorySource = InMemorySource(
            repository, parser=self.repository_parser
        )
         self.post_source: InMemorySource = InMemorySource(post, parser=self.post_parser)
         
    def __build_executor(self) -> None:
        self.executor = InMemoryExecutor(
            sources=[self.article_source, self.repository_source, self.post_source],
            indices=[self.article_index, self.repository_index, self.post_index],
        )

    def get_post_query(self, filters: dict) -> QueryObj:
        query = (
            Query(
                self.post_index,
                weights={
                    self.post_space_content: Param("content_weight"),
                    self.post_space_plaform: Param("platform_weight"),
                },
            )
            .find(post)
            .similar(self.post_space_content.text, Param("search_query"))
            .similar(self.post_space_plaform.category, Param("platform"))
            .limit(Param("limit"))
        )

        return self.__attach_filters(query, filters)

    def get_article_query(self, filters: dict) -> QueryObj:
        query = (
            Query(
                self.article_index,
                weights={
                    self.articles_space_content: Param("content_weight"),
                    self.articles_space_plaform: Param("platform_weight"),
                },
            )
            .find(article)
            .similar(self.articles_space_content.text, Param("search_query"))
            .similar(self.articles_space_plaform.category, Param("platform"))
            .limit(Param("limit"))
        )

        return self.__attach_filters(query, filters)

    def get_repository_query(self, filters: dict) -> QueryObj:
        query = (
            Query(
                self.repository_index,
                weights={
                    self.repository_space_content: Param("content_weight"),
                    self.repository_space_plaform: Param("platform_weight"),
                },
            )
            .find(repository)
            .similar(self.repository_space_content.text, Param("search_query"))
            .similar(self.repository_space_plaform.category, Param("platform"))
            .limit(Param("limit"))
        )

        return self.__attach_filters(query, filters)

    def __attach_filters(self, query_obj: QueryObj, filters: dict) -> QueryObj:
        for schema_field, value in filters.items():
            query_obj = query_obj.filter(schema_field == value)

        return query_obj

    def put(self, df: DataFrame, *, data_type: str) -> None:
        if data_type == "posts":
            self.post_source.put([df])
        elif data_type == "articles":
            self.article_source.put([df])
        elif data_type == "repositories":
            self.repository_source.put([df])
        else:
            raise RuntimeError(f"Unsupported data type: {data_type}")

    def query(
        self,
        text: str,
        *,
        platform: str | None = None,
        author_id: str | None = None,
        data_type: str,
        k: int = 3,
    ) -> DataFrame:
        query_kwargs = {
            "content_weight": 0.9,
            "platform_weight": 0.1,
            "search_query": text,
            "limit": k,
        }

        filters = {}
        if author_id:
            filters["author_id"] = author_id
        filters = self.__map_filter_to_schema(filters, data_type)
        
        if data_type == "posts":
            query_kwargs["query_obj"] = self.get_post_query(filters)
            query_kwargs["platform"] = platform if platform else "linkedin"
        elif data_type == "articles":
            query_kwargs["query_obj"] = self.get_article_query(filters)
            query_kwargs["platform"] = platform if platform else "medium"
        elif data_type == "repositories":
            query_kwargs["query_obj"] = self.get_repository_query(filters)
            query_kwargs["platform"] = platform if platform else "github"
        else:
            raise RuntimeError(f"Unsupported data type: {data_type}")

        result = self.app.query(**query_kwargs)

        return result.to_pandas()
    
    def __map_filter_to_schema(self, filters: dict, data_type: str) -> dict:
        mapped_filters = {}
        for key, value in filters.items():
            schema_key = getattr(schemas_repository[data_type], key)
            mapped_filters[schema_key] = value
            
        return mapped_filters
