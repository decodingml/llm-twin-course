from abc import ABC, abstractmethod

from models.clean import (
    ArticleCleanedModel,
    CleanedModel,
    PostCleanedModel,
    RepositoryCleanedModel,
)
from models.raw import ArticleRawModel, PostsRawModel, RawModel, RepositoryRawModel
from models.raw import ArticleRawModel, PostsRawModel, RawModel, RepositoryRawModel
from utils.cleaning import clean_text


class CleaningDataHandler(ABC):
    """
    Abstract class for all cleaning data handlers.
    All data transformations logic for the cleaning step is done here
    """

    @abstractmethod
    def clean(self, data_model: RawModel) -> CleanedModel:
        pass


class PostCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: PostsRawModel) -> PostCleanedModel:
        return PostCleanedModel(
            id=data_model.id,
            platform=data_model.platform,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: ArticleRawModel) -> ArticleCleanedModel:
        return ArticleCleanedModel(
            id=data_model.id,
            platform=data_model.platform,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class RepositoryCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: RepositoryRawModel) -> RepositoryCleanedModel:
        return RepositoryCleanedModel(
            id=data_model.id,
            platform=data_model.platform,
            name=data_model.name,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.owner_id,
            type=data_model.type,
        )
