# Introduction
This module is composed from 2 components:
- RAG component
- Finetuning dataset preparation component

# RAG component
A production RAG system is split into 3 main components:

    - ingestion: clean, chunk, embed, and load your data to a vector DB
    - retrieval: query your vector DB for context
    - generation: attach the retrieved context to your prompt and pass it to an LLM

The ingestion component sits in the feature pipeline, while the retrieval and generation components are implemented inside the inference pipeline.

You can also use the retrieval and generation components in your training pipeline to fine-tune your LLM further on domain-specific prompts.

You can apply advanced techniques to optimize your RAG system for ingestion, retrieval and generation.

That being said, there are 3 main types of advanced RAG techniques:

    - Pre-retrieval optimization [ingestion]: tweak how you create the chunks
    - Retrieval optimization [retrieval]: improve the queries to your vector DB
    - Post-retrieval optimization [retrieval]: process the retrieved chunks to filter out the noise

You can learn more about RAG from Decoding ML LLM Twin Course: 
- Lesson 4: [SOTA Python Streaming Pipelines for Fine-tuning LLMs and RAG — in Real-Time!](https://medium.com/decodingml/sota-python-streaming-pipelines-for-fine-tuning-llms-and-rag-in-real-time-82eb07795b87)
- Lesson 5: [The 4 Advanced RAG Algorithms You Must Know to Implement](https://medium.com/decodingml/the-4-advanced-rag-algorithms-you-must-know-to-implement-5d0c7f1199d2)

![Advanced RAG architecture](https://miro.medium.com/v2/resize:fit:720/format:webp/1*ui2cQRlRDVnKrXPXk7COLA.png "Advanced RAG architecture")


# Finetuning dataset preparation component
The finetuning dataset preparation module automates the generation of datasets specifically formatted for training and fine-tuning Large Language Models (LLMs). It interfaces with Qdrant, sends structured prompts to LLMs, and manages data with Comet ML for experiment tracking and artifact logging.

### Why is fine-tuning important?
1. **Model Customization**: Tailors the LLM's responses to specific domains or tasks.
2. **Improved Accuracy**: Enhances the model's understanding of nuanced language used in specialized fields.
3. **Efficiency**: Reduces the need for extensive post-processing by producing more relevant outputs directly.
4. **Adaptability**: Allows models to continuously learn from new data, staying relevant as language and contexts evolve.

TBD add about lesson
![Finetuning Dataset Preparation Flow](https://cdn-images-1.medium.com/max/800/1*gufpoEo92ZtuGQlVx6HVTw.png "Finetuning Dataset Preparation Flow")


# Dependencies
## Installation and Setup
To prepare your environment for these components, follow these steps:
- `poetry init`
- `poetry install`



## Docker Settings
### Host Configuration
To ensure that your Docker containers can communicate with each other you need to update your `/etc/hosts` file. 
Add the following entries to map the hostnames to your local machine:

```plaintext
# Docker MongoDB Hosts Configuration
127.0.0.1       mongo1
127.0.0.1       mongo2
127.0.0.1       mongo3
```

For the Windows users check this article: https://medium.com/workleap/the-only-local-mongodb-replica-set-with-docker-compose-guide-youll-ever-need-2f0b74dd8384

# CometML Integration

## Overview
[CometML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) is a cloud-based platform that provides tools for tracking, comparing, explaining, and optimizing experiments and models in machine learning. CometML helps data scientists and teams to better manage and collaborate on machine learning experiments.

## Why Use CometML?
- **Experiment Tracking**: CometML automatically tracks your code, experiments, and results, allowing you to compare between different runs and configurations visually.
- **Model Optimization**: It offers tools to compare different models side by side, analyze hyperparameters, and track model performance across various metrics.
- **Collaboration and Sharing**: Share findings and models with colleagues or the ML community, enhancing team collaboration and knowledge transfer.
- **Reproducibility**: By logging every detail of the experiment setup, CometML ensures experiments are reproducible, making it easier to debug and iterate.

## CometML Variables
When integrating CometML into your projects, you'll need to set up several environment variables to manage the authentication and configuration:

- `COMET_API_KEY`: Your unique API key that authenticates your interactions with the CometML API.
- `COMET_PROJECT`: The project name under which your experiments will be logged.
- `COMET_WORKSPACE`: The workspace name that organizes various projects and experiments.

## Obtaining CometML Variables

To access and set up the necessary CometML variables for your project, follow these steps:

1. **Create an Account or Log In**:
   - Visit [CometML's website](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) and log in if you already have an account, or sign up if you're a new user.

2. **Create a New Project**:
   - Once logged in, navigate to your dashboard. Here, you can create a new project by clicking on "New Project" and entering the relevant details for your project.

3. **Access API Key**:
   - After creating your project, you will need to obtain your API key. Navigate to your account settings by clicking on your profile at the top right corner. Select 'API Keys' from the menu, and you'll see an option to generate or copy your existing API key.

4. **Set Environment Variables**:
   - Add the obtained `COMET_API_KEY` to your environment variables, along with the `COMET_PROJECT` and `COMET_WORKSPACE` names you have set up.



# Qdrant Integration

## Overview
[Qdrant](https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course) is an open-source vector database designed for storing and searching large volumes of high-dimensional vector data. It is particularly suited for tasks that require searching through large datasets to find items similar to a query item, such as in recommendation systems or image retrieval applications.

## Why Use Qdrant?
Qdrant is a robust vector database optimized for handling high-dimensional vector data, making it ideal for machine learning and AI applications. Here are the key reasons for using Qdrant:

- **Efficient Searching**: Utilizes advanced indexing mechanisms to deliver fast and accurate search capabilities across high-dimensional datasets.
- **Scalability**: Built to accommodate large-scale data sets, which is critical for enterprise-level deployments.
- **Flexibility**: Supports a variety of distance metrics and filtering options that allow for precise customization of search results.
- **Integration with ML Pipelines**: Seamlessly integrates into machine learning pipelines, enabling essential functions like nearest neighbor searches.

## Setting Up Qdrant

[Qdrant](https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course) can be utilized via its Docker implementation or through its managed cloud service(https://cloud.qdrant.io/login). This flexibility allows you to choose an environment that best suits your project's needs.

### Environment Variables
To configure your environment for Qdrant, set the following variables:

## Docker Variables
- `QDRANT_HOST`: The hostname or IP address where your Qdrant server is running.
- `QDRANT_PORT`: The port on which Qdrant listens, typically `6333` for Docker setups.

## Qdrant Cloud Variables
- `QDRANT_CLOUD_URL`: The URL for accessing Qdrant Cloud services.
- `QDRANT_APIKEY`: The API key for authenticating with Qdrant Cloud.

Please check this article to learn how to obtain these variables (https://qdrant.tech/documentation/cloud/quickstart-cloud/)

Additionally, you can control the connection mode (Cloud or Docker) using a setting in your configuration file. More details can be found in db/qdrant.py :

```python
QDRANT_CLOUD: True  # Set to False to use Docker setup
```


**Before running any commands, ensure your environment variables are correctly set up in your `.env` file to guarantee that everything works properly.**

## Environment Configuration

Ensure your `.env` file includes the following configurations:

```plaintext
MONGO_DATABASE_HOST="mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set"
MONGO_DATABASE_NAME="scrabble"

# QdrantDB config
QDRANT_DATABASE_HOST="localhost"
QDRANT_DATABASE_PORT=6333
QDRANT_APIKEY= your-key
QDRANT_CLOUD_URL=your-url
QDRANT_CLOUD=False

# MQ config
RABBITMQ_DEFAULT_USERNAME=guest
RABBITMQ_DEFAULT_PASSWORD=guest
RABBITMQ_HOST=localhost
RABBITMQ_PORT= 5673

COMET_API_KEY="your-key"
COMET_WORKSPACE="alexandruvesa"
COMET_PROJECT='decodingml'

OPENAI_API_KEY = "your-key"
```

# Supplementary Tools
You need a real dataset to run and test the modules. 
This section covers additional tools and scripts included in the project that assist with specific tasks, such as data insertion.

## Script: `insert_data_mongo.py`

### Overview
The `insert_data_mongo.py` script is designed to manage the automated downloading and insertion of various types of documents (articles, posts, repositories) into a MongoDB database. It facilitates the initial population of the database with structured data for further processing or analysis.

### Features
- **Dataset Downloading**: Automatically downloads JSON formatted data files from Google Drive based on predefined file IDs.
- **Dynamic Data Insertion**: Inserts different types of documents (articles, posts, repositories) into the MongoDB database, associating each entry with its respective author.


### How It Works
1. **Download Data**: The script first checks if the specified `output_dir` directory exists and contains any files. If not, it creates the directory and downloads the data files from Google Drive.
2. **Insert Data**: Based on the type specified in the downloaded files, it inserts posts, articles, or repositories into the MongoDB database.
3. **Logging**: After each insertion, the script logs the number of items inserted and their associated author ID to help monitor the process.

# RAG Component


# RAG Module Structure
### Query Expansion
- `query_expansion.py`: Handles the expansion of a given query into multiple variations using language model-based templates. It integrates the `ChatOpenAI` class from `langchain_openai` and a custom `QueryExpansionTemplate` to generate expanded queries suitable for further processing.

### Reranking
- `reranking.py`: Manages the reranking of retrieved documents based on relevance to the original query. It uses a `RerankingTemplate` and the `ChatOpenAI` model to reorder the documents in order of relevance, making use of language model outputs.

### Retriever
- `retriever.py`: Performs vector-based retrieval of documents from a vector database using query expansion and reranking strategies. It utilizes the `QueryExpansion` and `Reranker` classes, as well as `QdrantClient` for database interactions and `SentenceTransformer` for generating query vectors.

### Self Query
- `self_query.py`: Generates metadata attributes related to a query, such as author ID, using a self-query mechanism. It employs a `SelfQueryTemplate` and the `ChatOpenAI` model to extract required metadata from the query context.

### Usage
After you have everything setup, environemnt variables, [CometML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) account and [Qdrant](https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course) account, it's time to insert data in your environment.

The workflow is straightforward:

- Start all the services: MongoDB, Qdrant, RabbitMQ
- Start the CDC system (for more details you can check https://medium.com/decodingml/the-3nd-out-of-11-lessons-of-the-llm-twin-free-course-ba82752dad5a)
- Insert data to mongodb by running  `make insert-data-mongo`
- Insert data into Qdrant VectorDB by running the [Bytewax](https://bytewax.io?utm_source=github&utm_medium=decodingml&utm_campaign=2024_q1) pipelines
- Go to retriver.py (outside of rag folder) and write your own query

The project includes a `Makefile` for easy management of common tasks. Here are the main commands you can use:

- `make help`: Displays help for each make command.
- `make local-start-infra`: Build and start mongodb, mq and qdrant.
- `make local-start-cdc`: Start cdc system
- `make insert-data-mongo`: Insert data to mongodb
- `make local-bytewax`: Run bytewax pipeline and send data to Qdrant
- `make local-test-retriever:-`: Test RAG retrieval


# Generate Data for LLM finetuning task component

# Component Structure


### File Handling
- `file_handler.py`: Manages file I/O operations, enabling reading and writing of JSON formatted data.

### LLM Communication
- `llm_communication.py`: Handles communication with OpenAI's LLMs, sending prompts and processing responses.

### Data Generation
- `generate_data.py`: Orchestrates the generation of training data by integrating file handling, LLM communication, and data formatting.


### Usage

The project includes a `Makefile` for easy management of common tasks. Here are the main commands you can use:

- `make help`: Displays help for each make command.
- `make local-start-infra`: Build and start mongodb, mq and qdrant.
- `make local-start-cdc`: Start cdc system
- `make insert-data-mongo`: Insert data to mongodb
- `make local-bytewax`: Run bytewax pipeline and send data to Qdrant
- `make generate-dataset`: Generate dataset for finetuning and version it in CometML



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
