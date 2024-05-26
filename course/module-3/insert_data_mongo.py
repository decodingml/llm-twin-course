import json
import re
from pathlib import Path

import gdown

import logger_utils
from db.documents import ArticleDocument, PostDocument, RepositoryDocument

logger = logger_utils.get_logger(__name__)


def fix_json_content(content: str) -> str:
    """
    Fixes common JSON escape errors in the provided content.
    """
    return re.sub(r'\\(?!["\\bfnrt/])', r"\\\\", content)


def download_dataset(output_dir: Path = Path("data")) -> list:
    files = [
        {
            "file_name": "articles_alex_vesa.json",
            "file_id": "1-82FgMIUR6UL5B7a7SHWOr3NnpTMbd-F",
            "type": "article",
            "author_id": "1",
        },
        {
            "file_name": "posts_alex_vesa.json",
            "file_id": "1HWvzvfyDRa50Dt-aLSonYHgGfY0JYulB",
            "type": "post",
            "author_id": "1",
        },
        {
            "file_name": "articles_paul_iusztin.json",
            "file_id": "1VAg4DdTK4zaRFJgX_5eGTaD-WwjxbG6z",
            "type": "article",
            "author_id": "2",
        },
        {
            "file_name": "posts_paul_iusztin.json",
            "file_id": "1hUeqVfh7nOTA1s_wv4PbDEc4sXU3TTmr",
            "type": "post",
            "author_id": "2",
        },
        {
            "file_name": "repositories_paul_iusztin.json",
            "file_id": "1tSWrlj_u85twAqVus-l0mzqgYVV6WHVz",
            "type": "repository",
            "author_id": "2",
        },
    ]
    for file in files:
        file["file_path"] = str(output_dir / file["file_name"])

    if output_dir.exists() and len(list(output_dir.iterdir())) > 0:
        logger.info("Directory already exists", directory=str(output_dir))

        return files
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        gdown.download(
            f"https://drive.google.com/uc?id={file['file_id']}",
            file["file_path"],
            quiet=False,
        )

    return files


def insert_posts(file_name: str, author_id: str) -> None:
    with open(file_name, "r") as file:
        posts: dict[str, dict] = json.load(file)

    for post_content in posts.values():
        try:
            PostDocument(
                platform="linkedin", content=post_content, author_id=author_id
            ).save()
        except:
            continue
    logger.info("Posts inserted into collection", num=len(posts), author_id=author_id)


def insert_articles(file_name: str, author_id: str) -> None:
    file_name = file_name
    try:
        with open(file_name, "r") as file:
            articles: list[dict] = json.load(file)
    except:
        with open(file_name, "r") as file:
            content = file.read()
            corrected_content = fix_json_content(content)
            articles: list[dict] = json.loads(corrected_content)

    for article_content in articles:
        try:
            ArticleDocument(
                platform="medium",
                link="/htttps/alex/paul",
                content=article_content,
                author_id=author_id,
            ).save()
        except:
            continue

    logger.info(
        "Articles inserted into collection", num=len(articles), author_id=author_id
    )


def insert_repositories(file_name: str, author_id: str) -> None:
    with open(file_name, "r") as file:
        respositores: dict[str, dict] = json.load(file)

        for repository_name, repository_content in respositores.items():
            RepositoryDocument(
                name=repository_name,
                link="/htttps/alex/paul",
                content=repository_content,
                owner_id=author_id,
            ).save()

    logger.info(
        "Repository inserted into collection",
        num=len(respositores),
        author_id=author_id,
    )


if __name__ == "__main__":
    output_dir = Path("./dataset")
    files = download_dataset(output_dir=output_dir)

    for file in files:
        match file["type"]:
            case "post":
                insert_posts(file["file_path"], file["author_id"])
            case "article":
                insert_articles(file["file_path"], file["author_id"])
            case "repository":
                pass
            case _:
                raise ValueError(f"Unknown type: {file['type']}")
