from typing import Optional

from pydantic import BaseModel, Field


class RepositoryRawModel(BaseModel):
    id: str = Field(alias="entry_id")
    type: str
    platform: str = "github"
    name: str
    link: str
    content: dict
    owner_id: str


class ArticleRawModel(BaseModel):
    id: str = Field(alias="entry_id")
    type: str
    platform: str
    link: str
    content: dict
    author_id: str


class PostsRawModel(BaseModel):
    id: str = Field(alias="entry_id")
    type: str
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None


RawModel = RepositoryRawModel | ArticleRawModel | PostsRawModel
