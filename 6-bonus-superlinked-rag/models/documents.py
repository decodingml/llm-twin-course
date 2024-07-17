from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator


class PostDocument(BaseModel):
    id: str
    platform: Annotated[str, BeforeValidator(str.lower)]
    content: str
    author_id: str
    type: str


class ArticleDocument(BaseModel):
    id: str
    platform: Annotated[str, BeforeValidator(str.lower)]
    link: str
    content: str
    author_id: str
    type: str


class RepositoryDocument(BaseModel):
    id: str
    platform: Annotated[str, BeforeValidator(str.lower)]
    name: str
    link: str
    content: str
    author_id: str
    type: str


Document = PostDocument | ArticleDocument | RepositoryDocument
