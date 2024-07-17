import pprint

from models.documents import ArticleDocument, PostDocument, RepositoryDocument
from superlinked_client import SuperlinkedClient

mock_data_articles = [
    ArticleDocument(
        id="1",
        platform="Twitter",
        link="http://twitter.com/1",
        content="Cleaned content 1",
        author_id="author_1",
        type="social",
    ),
    ArticleDocument(
        id="2",
        platform="Facebook",
        link="http://facebook.com/2",
        content="Cleaned content 2",
        author_id="author_2",
        type="social",
    ),
    ArticleDocument(
        id="3",
        platform="LinkedIn",
        link="http://linkedin.com/3",
        content="Cleaned content 3",
        author_id="author_3",
        type="professional",
    ),
    ArticleDocument(
        id="4",
        platform="Medium",
        link="http://medium.com/4",
        content="Cleaned content 4",
        author_id="author_4",
        type="blog",
    ),
    ArticleDocument(
        id="5",
        platform="Reddit",
        link="http://reddit.com/5",
        content="Cleaned content 5",
        author_id="author_5",
        type="forum",
    ),
]

mock_data_posts = [
    PostDocument(
        id="1",
        platform="Twitter",
        content="Cleaned content 1",
        author_id="author_1",
        type="social",
    ),
    PostDocument(
        id="2",
        platform="Facebook",
        content="Cleaned content 2",
        author_id="author_2",
        type="social",
    ),
    PostDocument(
        id="3",
        platform="LinkedIn",
        content="Cleaned content 3",
        author_id="author_3",
        type="professional",
    ),
    PostDocument(
        id="4",
        platform="Medium",
        content="Cleaned content 4",
        author_id="author_4",
        type="blog",
    ),
    PostDocument(
        id="5",
        platform="Reddit",
        content="Cleaned content 5",
        author_id="author_5",
        type="forum",
    ),
]

mock_data_repositories = [
    RepositoryDocument(
        id="1",
        platform="GitHub",
        name="Repo1",
        link="http://github.com/repo1",
        content="Cleaned content repo 1",
        author_id="owner_1",
        type="public",
    ),
    RepositoryDocument(
        id="2",
        platform="GitHub",
        name="Repo2",
        link="http://gitlab.com/repo2",
        content="Cleaned content repo 2",
        author_id="owner_2",
        type="private",
    ),
    RepositoryDocument(
        id="3",
        platform="GitHub",
        name="Repo3",
        link="http://bitbucket.com/repo3",
        content="Cleaned content repo 3",
        author_id="owner_3",
        type="public",
    ),
    RepositoryDocument(
        id="4",
        platform="GitHub",
        name="Repo4",
        link="http://github.com/repo4",
        content="Cleaned content repo 4",
        author_id="owner_4",
        type="public",
    ),
    RepositoryDocument(
        id="5",
        platform="GitHub",
        name="Repo5",
        link="http://gitlab.com/repo5",
        content="Cleaned content repo 5",
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
    pp = pprint.PrettyPrinter(indent=4)
    
    print("-" * 200)
    print("Article query:")
    pp.pprint(client.search_article("Cleaned content repo 4", "medium", author_id="author_4"))
    print("-" * 200)

    print("-" * 200)
    print("Post query:")
    pp.pprint(client.search_post("Cleaned content repo 4", "linkedin", author_id="author_4"))
    print("-" * 200)

    print("-" * 200)
    print("Repository query:")
    pp.pprint(client.search_repository("Cleaned content repo 4", "github", author_id="author_4"))
    print("-" * 200)
