from models.clean import ArticleCleanedModel, PostCleanedModel, RepositoryCleanedModel
from superlinked_client import SuperlinkedClient

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

if __name__ == "__main__":
    client = SuperlinkedClient("http://localhost:8080")

    # Ingest mock data.
    for article in mock_data_articles:
        client.ingest_article(article)
    for post in mock_data_posts:
        client.ingest_post(post)
    for repository in mock_data_repositories:
        client.ingest_repository(repository)

    # Query mock data.
    print("-" * 200)
    print("Article query:")
    print(client.search_article("Cleaned content repo 4", "medium", 3))
    print("-" * 200)

    print("-" * 200)
    print("Post query:")
    print(client.search_post("Cleaned content repo 4", "linkedin", 3))
    print("-" * 200)

    print("-" * 200)
    print("Repository query:")
    print(client.search_repository("Cleaned content repo 4", "github", 3))
    print("-" * 200)
