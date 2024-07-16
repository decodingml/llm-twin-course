# How to construct the app.py file

The application's main logic resides in the `app.py` file. This is where you define your application's structure and behavior using the Superlinked library.

By default, all examples within this documentation utilize an in-memory database. This configuration is optimal for testing and initial experimentation with the Superlinked framework. For detailed instructions on configuring and employing alternative vector databases, please refer to the [vector databases documentation.](vector_databases.md)

To start using the system, you can use the example application located [here](example/app.py).
You can find more complex examples how to construct the spaces and the queries in the [Superlinked notebooks](https://github.com/superlinked/superlinked/tree/main)

> Important Note: The `RecencySpace` feature is turned off by default due to the constraints of this release. For a detailed explanation and instructions on enabling it, refer to the [Using Recency Space](#using-recency-space) section of the documentation.

> Note: The primary aim of this document is to guide you on how to operate the Superlinked system with your preferred configuration, rather than explaining the inner workings of the Superlinked components. For a deeper understanding of the components, please refer to the notebooks mentioned above.

## Understanding the building blocks of the application

Here is a basic structure of an `app.py` file:
```python
# linked-file:dummy_app.py
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.dsl.executor.rest.rest_configuration import RestQuery
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase


@schema
class YourSchema:
    id: IdField
    attribute: String


your_schema = YourSchema()

text_space = TextSimilaritySpace(text=your_schema.attribute, model="model-name")

index = Index(text_space)

query = (
    Query(index)
    .find(your_schema)
    .similar(
        text_space.text,
        Param("query_text"),
    )
)

your_source: RestSource = RestSource(your_schema)

executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
```

In this example, we define a schema for our data, create a text similarity space, define an index, and set up a query. We then create a REST source and an executor that uses this source, the index, and the query.


You can find more detailed information and examples of various features in the [Superlinked feature notebooks](https://github.com/superlinked/superlinked/tree/main/notebook/feature). The [basic_building_blocks.ipynb](https://github.com/superlinked/superlinked/blob/main/notebook/feature/basic_building_blocks.ipynb) notebook provides a comprehensive guide on the basic structure and how to use it, while the other notebooks cover various features of the Superlinked library.

In this deployment setup, you are not required to define any computations as you would in the [basic_building_blocks.ipynb](https://github.com/superlinked/superlinked/blob/main/notebook/feature/basic_building_blocks.ipynb) notebook. Instead, your focus will be on defining the schema, the text similarity space, the index, the query, the REST source, and the executor.

The `app.py` file ends with adding the executor to the `SuperlinkedRegistry`. Use SuperlinkedRegistry to register your components for production, this is not required when experimenting with InMemoryExecutor. If you've got more than one executor, you can add them all at once, separated by commas, like this: `SuperlinkedRegistry.register(executor1, executor2, executor3)`. 
The executor is the component that executes the queries defined in your application, utilizing the sources, indices, and queries you have established. Here's an example of how to define an executor:
```python
executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
```
In this example, `your_source` is the REST source you've defined, `index` is the index you've created, and `query` is the query you've set up. The `RestQuery` function wraps your query with a `RestDescriptor`, which provides a name for your query that can be used to call it from the REST API. In the preceding example, the path is set to `/api/v1/search/query`. This is where you assign a name to the final segment of the path, assuming you are using the default settings. [More detailed API info](#customize-your-api)

This setup abstracts away the need for explicit computation definition, allowing you to concentrate on defining your application's structure and behavior. The Superlinked library handles the rest, executing your queries and returning the results when the application is run. This approach allows you to make changes to your application without needing to SSH into the server and edit the `app.py` file in the directory with each change.

Remember to replace the placeholders in the example with your actual data and requirements. The `app.py` file should be stored in an S3 bucket (if you're using AWS) or a GCS bucket (if you're using GCP). This setup allows you to make changes to your application without needing to SSH into the server and edit the `app.py` file in the directory with each change. 

## Configuring the data loader

The system has a feature to load data from file(s) either from local or remote.

> Note: In the absence of specified chunking, the loader will attempt to read and load the entire file into the system by default. Mind your memory! If possible, utilize file formats that support chunking and include the necessary parameters in the `pandas_read_kwargs` as indicated below.

Constraints: 
- When running your preview locally, only local files or public ones from remote sources can be used. Targeting an S3 bucket or GCP that requires authentication is not possible.
- When running in the cloud, for example on GCP, you can target private Google Cloud Storage (GCS) bucket but only those that the Google Cloud Engine (GCE) instance has access to. 
  It will utilize its own authentication and authorization, but no other private cloud sources like S3 can be used. Local files on the GCE or any public file that doesn't require authorization can also be used.

### Incorporate Data Source

Create a specific source that can point to a local or a remote file. This file can be parsed and loaded into the system more efficiently than invoking the REST endpoint for each piece of data:
```python
# The path can be a local file, a remote. The available DataFormats are: [JSON, CSV, PARQUET, ORC, XML, FWF]
# The `name_of_your_loader` is an optional parameter, which is the identifier of your loader. Read more about it below the code block.
# The last argument is a pass through argument that pandas should be able to use so use the format that is compatible with pandas.
# Note: the pandas_read_kwargs is an optional parameter, if you don't need any customization, it will use the defaults.
config = DataLoaderConfig("https://path-to-your-file.csv", DataFormat.CSV, "name_of_your_loader", pandas_read_kwargs={"sep": ";"})
data_loader_source = DataLoaderSource(your_schema, config) # Add your config to the source. This is mandatory.

executor = RestExecutor(
    sources=[your_source, data_loader_source], # Incorporate the data_loader_source into the sources here.
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)
```

> Name of your data loader: The `name` parameter in `DataLoaderConfig` is optional. By default, it adopts the snake_case version of your schema's name used in `DataLoaderSource`. If you have multiple data loaders for the same schema or prefer a different name, simply set the `name` parameter accordingly.
> Note that the name will always be converted to snake_case. To see the configured data loaders in your system, refer to the [API documentation](api.md#see-available-data-loaders).

The data loader is now configured but **it only runs if you send a request to the data loader endpoint!** To see how to trigger it, check the API documentation [here](api.md#trigger-the-data-load)

## Optional steps

### Schema to column mappings

By default, the system will attempt to parse your file, hence the column names should align with your schema attributes. If an `id` column has a different name for example, as well as the other schema fields, it needs to be mapped to the schema you are attempting to load. To map field names to your schema, utilize the data parser as shown below:
```python
# Instantiate a DataFrameParser object, composed of the schema you wish to map and the actual mapping. The format for mapping is: `<schema.field>: <column_name>`
# Note: If the column names are exactly the same (case sensitive) as your schema, you don't need to provide a parser for the source at all.
data_frame_parser = DataFrameParser(your_schema, mapping={your_schema.id: "id_field_name", your_schema.attribute: "custom_field_name"})
data_loader_source = DataLoaderSource(your_schema, config, data_frame_parser) # Incorporate the parser into your source
```

### Data Chunking

Data chunking allows you to load more data than your memory could typically handle at once. This is particularly beneficial when dealing with data sets that span multiple gigabytes.
> If you're uncertain whether your data will fit into your memory, it's strongly advised to employ chunking to prevent unexpected problems. By setting the [log level to debug in the executor](../runner/executor/.env), you can view pandas memory information regardless of whether you're chunking the data. This assists in estimating memory usage.

To implement chunking, you'll need to use either CSV or JSON formats (specifically JSONL, which includes JSON objects on each line).

Here's an example of what a chunking configuration might look like:
```python
# For CSV
config = DataLoaderConfig("https://path-to-your-file.csv", DataFormat.CSV, pandas_read_kwargs={"chunksize": 10000})
# For JSON
config = DataLoaderConfig("https://path-to-your-file.jsonl", DataFormat.JSON, pandas_read_kwargs={"lines": True, "chunksize": 10000})
```

The Superlinked library performs internal batching for embeddings, with a default batch size of 10000. If you are utilizing a chunk size different from 10000, it is advisable to adjust this batch size to match your chunk size.
To modify this, alter the `INMEMORY_PUT_CHUNK_SIZE` value [in this file](../runner/executor/.env)

### Customize your API

If you want to configure your API path, you can do that with the `RestEndpointConfiguration`, which can alter your URL. By default the API looks like:
- Query endpoint's path is: `/api/v1/search/<query_name>` which aligns with the schema: `/<api_root_path>/<query_path_prefix>/<query_name>` 
- Data ingestion endpoint's path is: `/api/v1/ingest/<schema_name>` which aligns with the schema: `/<api_root_path>/<ingest_path_prefix>/<schema_name>`
- The rest of the API is non configurable, that is part of the so called, management API.

To change the API's default path, see the following code, that let's you customize it:
```python
rest_endpoint_config = RestEndpointConfiguration(
    query_path_prefix="retrieve",
    ingest_path_prefix="insert",
    api_root_path="/superlinked/v3",
) # This will change the root path for both ingest and query endpoints

executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
    rest_endpoint_config=rest_endpoint_config # Incorporate your config here
)
```

### Using Recency Space

Recency Space has two current limitations:
- Recency embeddings become outdated over time as they are not recalculated periodically. Our encoder only needs a constant number of updates for this to work correctly, but that update mechanism has not been open-sourced yet - coming soon!
- At server startup, the application captures the server's current UTC timestamp as `now`. During development, each modification and restart of the application will result in a new timestamp, which makes results irreproducible within restarts.

The first one is a known limitation that will be fixed in the near future. The second one can be solved with setting the timestamp to a fixed value.
```python
NOW = int(datetime(year=2024, month=1, day=2, tzinfo=UTC).timestamp()) # Here you can set the exact date to work with. Note: you can set hours, minute and so on.
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: NOW}} # Then use the following dict structure
```

Then add the `EXECUTOR_DATA` to your executor, like:

```python
executor = RestExecutor(
    sources=[source], indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
    context_data=EXECUTOR_DATA, # Add your executor data here
)
```

Finally, you need to set a flag to prevent exceptions when utilizing Recency Space. Set the `DISABLE_RECENCY_SPACE` flag to `false` in the [.env config file](../runner/executor/.env)

