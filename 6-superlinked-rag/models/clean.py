from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator


class PostCleanedModel(BaseModel):
    id: str
    platform: Annotated[str, BeforeValidator(str.lower)]
    cleaned_content: str
    author_id: str
    type: str


class ArticleCleanedModel(BaseModel):
    id: str
    platform: Annotated[str, BeforeValidator(str.lower)]
    link: str
    cleaned_content: str
    author_id: str
    type: str


class RepositoryCleanedModel(BaseModel):
    id: str
    platform: Annotated[str, BeforeValidator(str.lower)]
    name: str
    link: str
    cleaned_content: str
    author_id: str
    type: str


CleanedModel = PostCleanedModel | ArticleCleanedModel | RepositoryCleanedModel
