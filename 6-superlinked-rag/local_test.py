from models import utils as model_utils
from models.clean import ArticleCleanedModel, PostCleanedModel, RepositoryCleanedModel
from superlinked_engine import SuperlinkedEngine

mock_data_articles = [
    ArticleCleanedModel(
        id="1",
        platform="Twitter",
        link="http://twitter.com/1",
        cleaned_content="Cleaned content 1",
        author_id="author_1",
        type="social",
    ),
    ArticleCleanedModel(
        id="2",
        platform="Facebook",
        link="http://facebook.com/2",
        cleaned_content="Cleaned content 2",
        author_id="author_2",
        type="social",
    ),
    ArticleCleanedModel(
        id="3",
        platform="LinkedIn",
        link="http://linkedin.com/3",
        cleaned_content="Cleaned content 3",
        author_id="author_3",
        type="professional",
    ),
    ArticleCleanedModel(
        id="4",
        platform="Medium",
        link="http://medium.com/4",
        cleaned_content="Cleaned content 4",
        author_id="author_4",
        type="blog",
    ),
    ArticleCleanedModel(
        id="5",
        platform="Reddit",
        link="http://reddit.com/5",
        cleaned_content="Cleaned content 5",
        author_id="author_5",
        type="forum",
    ),
]
articles_df = model_utils.pydantic_models_to_dataframe(mock_data_articles)

mock_data_posts = [
    PostCleanedModel(
        id="1",
        platform="Twitter",
        cleaned_content="Cleaned content 1",
        author_id="author_1",
        type="social",
    ),
    PostCleanedModel(
        id="2",
        platform="Facebook",
        cleaned_content="Cleaned content 2",
        author_id="author_2",
        type="social",
    ),
    PostCleanedModel(
        id="3",
        platform="LinkedIn",
        cleaned_content="Cleaned content 3",
        author_id="author_3",
        type="professional",
    ),
    PostCleanedModel(
        id="4",
        platform="Medium",
        cleaned_content="Cleaned content 4",
        author_id="author_4",
        type="blog",
    ),
    PostCleanedModel(
        id="5",
        platform="Reddit",
        cleaned_content="Cleaned content 5",
        author_id="author_5",
        type="forum",
    ),
]
posts_df = model_utils.pydantic_models_to_dataframe(mock_data_posts)

mock_data_repositories = [
    RepositoryCleanedModel(
        id="1",
        platform="GitHub",
        name="Repo1",
        link="http://github.com/repo1",
        cleaned_content="Cleaned content repo 1",
        author_id="owner_1",
        type="public",
    ),
    RepositoryCleanedModel(
        id="2",
        platform="GitHub",
        name="Repo2",
        link="http://gitlab.com/repo2",
        cleaned_content="Cleaned content repo 2",
        author_id="owner_2",
        type="private",
    ),
    RepositoryCleanedModel(
        id="3",
        platform="GitHub",
        name="Repo3",
        link="http://bitbucket.com/repo3",
        cleaned_content="Cleaned content repo 3",
        author_id="owner_3",
        type="public",
    ),
    RepositoryCleanedModel(
        id="4",
        platform="GitHub",
        name="Repo4",
        link="http://github.com/repo4",
        cleaned_content="Cleaned content repo 4",
        author_id="owner_4",
        type="public",
    ),
    RepositoryCleanedModel(
        id="5",
        platform="GitHub",
        name="Repo5",
        link="http://gitlab.com/repo5",
        cleaned_content="Cleaned content repo 5",
        author_id="owner_5",
        type="private",
    ),
]
repositories_df = model_utils.pydantic_models_to_dataframe(mock_data_repositories)

if __name__ == "__main__":
    print("Running using engine!")

    engine = SuperlinkedEngine()
    engine.put(articles_df, data_type="articles")
    engine.put(posts_df, data_type="posts")
    engine.put(repositories_df, data_type="repositories")

    print("Articles:")
    article_results = engine.query(
        "Cleaned content 1", author_id="author_3", data_type="articles"
    )
    print(article_results)
    print("-" * 100)

    print("Posts:")
    post_results = engine.query("Cleaned content 1", data_type="posts")
    print(post_results)
    print("-" * 100)
