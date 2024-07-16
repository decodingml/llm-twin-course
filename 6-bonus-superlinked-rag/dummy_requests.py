import httpx

from models.clean import RepositoryCleanedModel

# Define the URL
url = 'http://localhost:8080/api/v1/ingest/repository_schema'

# Define the headers
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json'
}

data = RepositoryCleanedModel(
        id="1",
        platform="GitHub",
        name="Repo1",
        link="http://github.com/repo1",
        cleaned_content="Cleaned content repo 1",
        author_id="owner_1",
        type="public",
    )
data = data.model_dump()


# Make the POST request
response = httpx.post(url, headers=headers, json=data)

# Print the response status code and content
print(response.status_code)


url = 'http://localhost:8080/api/v1/search/repository_query'

# Define the headers
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json'
}

# Define the data payload
data = {
    "search_query": "your_search_text",
    "platform": "github",
    "limit": 3
}

# Make the POST request
response = httpx.post(url, headers=headers, json=data)

# Print the response status code and content
print(response.status_code)
print(response.json())
