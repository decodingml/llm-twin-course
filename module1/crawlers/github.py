import os
import shutil
import subprocess
import tempfile

from crawlers.base import BaseCrawler
from documents import RepositoryDocument


class GithubCrawler(BaseCrawler):

    model = RepositoryDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")):
        super().__init__()
        self._ignore = ignore

    def extract(self, link: str, **kwargs):
        repo_name = link.rstrip("/").split("/")[-1]

        local_temp = tempfile.mkdtemp()

        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")

            instance = self.model(name=repo_name, link=link, content=tree, owner_id=kwargs.get("user"))
            instance.save()

        except Exception:
            raise
        finally:
            shutil.rmtree(local_temp)


def handler(event, context):
    # Extract the necessary information from the event object
    link = os.getenv("repository_link")
    user = os.getenv("user")

    # Instantiate the GithubCrawler
    crawler = GithubCrawler()

    try:
        # Use the crawler to extract data from the repository
        crawler.extract(link=link, user=user)

        return {"statusCode": 200, "body": "Repository processed successfully"}

    except Exception as e:
        # Handle exceptions
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


# Example of Usage
if __name__ == "__main__":
    crawler = GithubCrawler()
    crawler.extract(link="git@github.com:decodingml/llm-twin-course.git", user="Alex")
