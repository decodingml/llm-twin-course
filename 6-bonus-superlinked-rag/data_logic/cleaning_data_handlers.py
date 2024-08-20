from abc import ABC, abstractmethod

from models.documents import ArticleDocument, Document, PostDocument, RepositoryDocument
from models.raw import ArticleRawModel, PostsRawModel, RawModel, RepositoryRawModel
from utils.cleaning import clean_text

from .splitters import split_text


class CleaningDataHandler(ABC):
    """
    Abstract class for all cleaning data handlers.
    All data transformations logic for the cleaning step is done here
    """

    @abstractmethod
    def clean(self, data_model: RawModel) -> list[Document]:
        pass


class PostCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: PostsRawModel) -> list[PostDocument]:
        documents = []
        cleaned_text = clean_text("".join(data_model.content.values()))
        for post_subsection in split_text(cleaned_text):
            documents.append(
                PostDocument(
                    id=data_model.id,
                    platform=data_model.platform,
                    content=post_subsection,
                    author_id=data_model.author_id,
                    type=data_model.type,
                )
            )

        return documents


class ArticleCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: ArticleRawModel) -> list[ArticleDocument]:
        documents = []
        cleaned_text = clean_text("".join(data_model.content.values()))
        for article_subsection in split_text(cleaned_text):
            documents.append(
                ArticleDocument(
                    id=data_model.id,
                    platform=data_model.platform,
                    link=data_model.link,
                    content=article_subsection,
                    author_id=data_model.author_id,
                    type=data_model.type,
                )
            )

        return documents


class RepositoryCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: RepositoryRawModel) -> list[RepositoryDocument]:
        documents = []
        for file_name, file_content in data_model.content.items():
            cleaned_file_content = clean_text(file_content)
            for file_subsection in split_text(cleaned_file_content):
                documents.append(
                    RepositoryDocument(
                        id=data_model.id,
                        platform=data_model.platform,
                        name=f"{data_model.name}:{file_name}",
                        link=data_model.link,
                        content=file_subsection,
                        author_id=data_model.owner_id,
                        type=data_model.type,
                    )
                )

        return documents
