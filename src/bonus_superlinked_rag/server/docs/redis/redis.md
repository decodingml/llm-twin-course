# Redis

This document provides clear steps on how to use and integrate Redis with Superlinked.

## Configuring your existing managed Redis

To use Superlinked with Redis, you will need several Redis modules. The simplest approach is to use the official Redis Stack, which includes all the necessary modules. Installation instructions for the Redis Stack can be found in the [Redis official documentation](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/). Alternatively, you can start a managed instance provided by Redis (a free-tier is available). For detailed steps on initiating a managed instance, refer to the [Start a Managed Redis Instance](#start-a-managed-redis-instance) section below.

Once your Redis instance is up and running, ensure it is accessible from the server that will use it. Additionally, configure the necessary authentication settings as described below.

## Modifications in app.py

To integrate Redis, you need to add the `RedisVectorDatabase` class and include it in the executor. Here’s how you can do it:

To configure your Redis, the following code will help you:
```python
from superlinked.framework.dsl.storage.redis_vector_database import RedisVectorDatabase

vector_database = RedisVectorDatabase(
    "<your_redis_host>", # (Mandatory) This is your redis URL without any port or extra fields
    12315, # (Mandatory) This is the port and it should be an integer
    # These params must be in a form of kwarg params. Here you can specify anything that the official python client 
    # enables. The params can be found here: https://redis.readthedocs.io/en/stable/connections.html. Below you can see a very basic user-pass authentication as an example.
    username="test",
    password="password"
)
```

Once you have configured the vector database just simply set it as your vector database.
```python
...
executor = RestExecutor(
    sources=[source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=vector_database, # Or any variable that you assigned your `RedisVectorDatabase`
)
...
```

## Start a Managed Redis Instance

To initiate a managed Redis instance, navigate to [Redis Labs](https://app.redislabs.com/), sign in, and click the "New Database" button. On the ensuing page, locate the `Type` selector, which offers two options: `Redis Stack` and `Memcached`. By default, `Redis Stack` is pre-selected, which is the correct choice. If it is not selected, ensure to choose `Redis Stack`. For basic usage, no further configuration is necessary. Redis already generated a user which called `default` and a password that you can see below it. However, if you intend to use the instance for persistent data storage beyond sandbox purposes, consider configuring High Availability (HA), data persistence, and other relevant settings.

## Example app with Redis

You can find an example that utilizes Redis [here](app_with_redis.py)

