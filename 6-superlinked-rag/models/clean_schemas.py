from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String


@schema
class PostCleanedSchema:
    id: IdField
    platform: String
    cleaned_content: String
    author_id: String
    type: String


@schema
class ArticleCleanedSchema:
    id: IdField
    platform: String
    link: String
    cleaned_content: String
    author_id: String
    type: String


@schema
class RepositoryCleanedSchema:
    id: IdField
    name: String
    link: String
    cleaned_content: String
    owner_id: String
    type: String


post = PostCleanedSchema()
article = ArticleCleanedSchema()
repository = RepositoryCleanedSchema()
