from typing import Optional

from models.base import DataModel


class RepositoryRawModel(DataModel):
    name: str
    link: str
    content: dict
    owner_id: str


class ArticleRawModel(DataModel):
    platform: str
    link: str
    content: dict
    author_id: str


class PostsRawModel(DataModel):
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None
