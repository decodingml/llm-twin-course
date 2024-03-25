from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from crawlers import GithubCrawler, LinkedInCrawler, MediumCrawler
from dispatcher import CrawlerDispatcher
from documents import UserDocument

logger = Logger(service="decodingml/crawler")

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", MediumCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)


def handler(event, context: LambdaContext) -> dict[str, Any]:

    first_name, last_name = event.get("user").split(" ")
    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")
    crawler = _dispatcher.get_crawler(link)

    try:
        crawler.extract(link=link, user=user)

        return {"statusCode": 200, "body": "Articles processed successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    event = {
        "user": "Paul Iuztin",
        "link": "https://github.com/iusztinpaul/hands-on-llms",
    }
    handler(event, None)
