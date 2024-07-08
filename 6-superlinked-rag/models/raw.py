from typing import Optional

from pydantic import BaseModel


class RepositoryRawModel(BaseModel):
    name: str
    link: str
    content: dict
    owner_id: str


class ArticleRawModel(BaseModel):
    platform: str
    link: str
    content: dict
    author_id: str


class PostsRawModel(BaseModel):
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None
