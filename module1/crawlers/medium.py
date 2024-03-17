from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from crawlers.base import BaseAbstractCrawler
from documents import ArticleDocument


class MediumCrawler(BaseAbstractCrawler):

    model = ArticleDocument

    def set_driver_options(self) -> Options:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-data-dir=/Users/ristoc/Library/Application Support/Google/Chrome")
        options.add_argument(r"--profile-directory=Profile 2")

        return options

    def extract(self, link: str, **kwargs):
        self.driver.get(link)
        self.scroll_page()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        title = soup.find_all("h1", class_="pw-post-title")
        subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }

        print(f"Successfully scraped and saved articles for user {link}")
        self.driver.close()
        instance = self.model(platform="medium", content=data, link=link, author_id=kwargs.get("user"))
        instance.save()

    def login(self):
        """Log in to Medium with Google"""
        self.driver.get("https://medium.com/m/signin")  # TODO set as static parameter
        self.driver.find_element(By.TAG_NAME, "a").click()
