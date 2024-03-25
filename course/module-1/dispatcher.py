import re

from crawlers.base import BaseCrawler


class CrawlerDispatcher:

    def __init__(self):
        self._crawlers = {}

    def register(self, domain: str, crawler: type[BaseCrawler]):
        self._crawlers[r"https://(www\.)?{}.com/*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        else:
            raise ValueError("No crawler found for the provided link")
