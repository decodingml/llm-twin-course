# Using the API to ingest and query the application

Once you have your application up and running, you can start loading data and querying the API. Here's a step-by-step guide on how to do it:

## Ingest an entry

1. **Data Ingestion**: You can test data ingestion by making a POST request to the `/api/v1/ingest/your_schema` endpoint. Here's an example using `curl`:
    ```bash
    curl -X POST \
        'http://localhost:8080/api/v1/ingest/your_schema' \
        --header 'Accept: */*' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "id": "your_id",
            ...
        }'
    ```
    > **Note**: The current example will not work, please change the request body as your schema requires it.

## Query your system

1. **Query the API**: After ingesting data, you can query the API by making a POST request to the `/api/v1/search/query` endpoint. Here's an example using `curl`:
    ```bash
    curl -X POST \
        'http://localhost:8080/api/v1/search/query' \
        --header 'Accept: */*' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "query_text": "your_search_text"
        }'
    ```
This request will search for entities that match the query text.

## Load data from file(s)

### See available data loaders

To see what data loaders are available, send a request to the endpoint below:

```bash
curl 'http://localhost:8080/data-loader/'
```
Successful response (200 OK):
```JSON
{
    "result": [
        "<NAME_OF_YOUR_DATA_LOADER>": "DataLoaderConfig(path='https://path-to-your-file.csv', format=<DataFormat.CSV: 2>, name=None, pandas_read_kwargs='{sep: ;}')"
    ]
}
```

> The keys are the available data loader names that you can use for the rest of the data loader endpoints below. To see how these names are constructed and can be altered, read the [docs here](app.md#incorporate-data-source).

### Trigger the data load

To initiate the data load, invoke its endpoint. This will spawn an asynchronous task `DataLoaderSource` by its name as defined in your `app.py`. To trigger the endpoint, simply send a request with `curl` as shown below. The response should be 202 Accepted.
If the name you provided is not found in the system, a 404 NOT FOUND will be returned. If you try to start it while it is already running, a 409 CONFLICT will be returned.

```bash
curl -X POST 'http://localhost:8080/data-loader/<NAME_OF_YOUR_DATA_LOADER>/run'
```
Successful response (200 OK):
```JSON
{
    "result": "Background task successfully started with name: <NAME_OF_YOUR_DATA_LOADER>",
}
```

### See the status of your tasks

To check if your data is still being loaded to the system, you can trigger the status endpoint. The endpoint needs the name of your data loader. If you have multiple of them, you need to send one request for each task. The endpoint will return with 200 if the given task exists in the system and 404 if not. The response will be a JSON with a human readable explanation what happened. If it failed, you still get a 200 with details in the body.

```bash
curl -X GET 'http://localhost:8080/data-loader/<NAME_OF_YOUR_DATA_LOADER>/status
```
Successful response (200 OK):
```JSON
{
    "result": "Task is still running",
}
```
If the data loader is not found by its name in the system (404 Not found):
```JSON
{
    "result": "Task not found with name: <NAME_OF_YOUR_DATA_LOADER>",
}
```
