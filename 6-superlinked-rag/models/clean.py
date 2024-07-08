from pydantic import BaseModel


class PostCleanedModel(BaseModel):
    id: str
    platform: str
    cleaned_content: str
    author_id: str
    type: str


class ArticleCleanedModel(BaseModel):
    id: str
    platform: str
    link: str
    cleaned_content: str
    author_id: str
    type: str


class RepositoryCleanedModel(BaseModel):
    id: str
    name: str
    link: str
    cleaned_content: str
    owner_id: str
    type: str
