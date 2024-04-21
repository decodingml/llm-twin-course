# Module 4: RAG Retrieval


# Introduction:
This chapter focuses on the retrival component of a RAG system, meaning the part where we search the vector DB for relevant information given a user query as input.


Retrival in a RAG system is a crucial component because the data that we extract will be later used as context for a LLM to answer questions.
Depending on the techniques used here the coherence and relevance of the response can vary greatly, a naive RAG often times won't do the trick.
Here we chose to implement different methods of doing queries on the vector DB as well as some pre- / post-processing work on the data.
    
    1. Self-Query implementation using LLM
    2. Metadata filtering
    3. Pre-processing: Query expansion technique
    4. Post-processing: Reranking using prompt engineering

# The module structure
## LLM Components
Singleton class to manage langchain chains
- `chain.py`

Collection of classes (including base) of prompt templates for managing the chain input
- `prompt_templates.py`

## query_expansion.py
- **Functionality**: Singleton class that uses langchain to feed a user query to a LLM, that also receives a prompt instructing it to create 5 sub queries for the initial one using different perspectives.

## self_query.py
- **Functionality**: Singleton class that uses langchain to feed a user query to a LLM, that also receives a prompt instructing it to extract metadata keys and values form the given user query.
- **Metadata filter**: The values extracted from the LLM response will be used to filter the retrieved vectors.

## reranking.py

- **Functionality**: Singleton class that uses langchain to feed a user query and a list of retrieved passages to a LLM, that also receives a prompt instructing it to rearrange them based on their relevancy related to the given user prompt

## retriever.py
- **Functionality**: Singleton class to manage the hole retrival process using the other classes as components and multy-threading at search.

## test_retriever.py
This script is created in order to see the retried data from the DB. In order to test this all the previous test steps from the previous modules need to be completed and the docker containers to be still running. Also additional data need's to be added to the DB using the step's from module 2/3

# Installation and Setup
To set up the environment for this project, follow these steps:

1. **Install Dependencies**: Run `poetry install` to install the required dependencies.
2. **Environment Variables**: Use the `.env.example` file as a template to create your `.env` file. This file should include configurations for MongoDB and RabbitMQ, like the host, port, and credentials.
   
   Example variables:
   - MongoDB Configuration (MONGO_DATABASE_HOST, MONGO_DATABASE_NAME)
   - RabbitMQ Configuration (RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_DEFAULT_USERNAME, RABBITMQ_DEFAULT_PASSWORD)

Ensure you replace the example values with your specific configuration details.

# Docker Configuration
The project includes a `docker-compose.yaml` file to manage the Docker containers for MongoDB and RabbitMQ. Here’s an overview of the configuration:

- **MongoDB Replica Set**: Configures three MongoDB containers (`mongo1`, `mongo2`, `mongo3`) as a replica set for redundancy and high availability.
- **RabbitMQ**: Sets up a RabbitMQ container with management capabilities.
- **Volumes and Ports**: Defines specific ports and volumes for each service to ensure persistent storage and accessibility.
- **Healthcheck**: Includes a healthcheck for MongoDB to ensure the containers are functioning correctly.

# Usage

The project includes a Makefile for easy management of common tasks. Here are the main commands you can use:

- `make help`: Displays help for each make command.
- `make local-start-infra`: Builds and starts MongoDB and RabbitMQ using Docker. This prepares the necessary services for the CDC system.
- `make local-stop-ifra`: Stops the docker containers.
- `make local-run-test`: Start's the retrieving process and the retrieved data should be printed to the console.


# Cloud environment
TBD



# Meet your teachers!
The course is created under the [Decoding ML](https://decodingml.substack.com/) umbrella by:

<table>
  <tr>
    <td><a href="https://github.com/iusztinpaul" target="_blank"><img src="https://github.com/iusztinpaul.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Paul Iusztin</strong><br />
      <i>Senior ML & MLOps Engineer</i>
    </td>
  </tr>
  <tr>
    <td><a href="https://github.com/alexandruvesa" target="_blank"><img src="https://github.com/alexandruvesa.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Alexandru Vesa</strong><br />
      <i>Senior AI Engineer</i>
    </td>
  </tr>
  <tr>
    <td><a href="https://github.com/Joywalker" target="_blank"><img src="https://github.com/Joywalker.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Răzvanț Alexandru</strong><br />
      <i>Senior ML Engineer</i>
    </td>
  </tr>
</table>

# License

This course is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., university projects, college degree projects, personal projects, etc.).

# 🏆 Contribution

A big "Thank you 🙏" to all our contributors! This course is possible only because of their efforts.

<p align="center">
    <a href="https://github.com/decodingml/llm-twin-course/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=decodingml/llm-twin-course" />
    </a>
</p>