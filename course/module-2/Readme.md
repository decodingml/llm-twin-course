# Module 2: Change Data Capture: Enabling Event-Driven Architecture


# Introduction
Change Data Capture, commonly known as CDC, is an efficient way to track changes in a database.

The purpose of CDC is to capture insertions, updates, and deletions applied to a database and to make this change data available in a format easily consumable by downstream applications.
Why do we need CDC pattern?

    1. Real-time Data Syncing: CDC facilitates near-real-time data integration and syncing.
    2. Efficient Data Pipelines: It allows incremental data loading, which is more efficient than bulk load operations.
    3. Minimized System Impact: CDC minimizes the impact on the source system by reducing the need for performance-intensive queries.
    4. Event-Driven Architectures: It enables event-driven architectures by streaming database events.


# The module structure
## Data Flow Module
Singleton class to manage RabbitMQ connection.
- `mq.py`

## DB Module
Singleton class to connect to MongoDB database.
- `mongo.py`

## cdc.py
- **Functionality**: This script sets up a CDC pipeline. It monitors a MongoDB database for changes and forwards these changes to a RabbitMQ message queue.
- **MongoDB Connection**: It connects to a MongoDB database (specifically the "scrabble" collection), utilizing a class from `db.mongo`.
- **Change Tracking**: The script watches for insert operations in MongoDB. When a change is detected, it processes and serializes the change details.
- **Data Processing**: Each change's metadata is extracted and serialized using `json_util`. The `_id` field is converted to a string and additional metadata is added.
- **RabbitMQ Integration**: After serialization, the script publishes the data to a RabbitMQ queue named "test_queue".

## test_cdc.py
This script is designed to test the MongoDB database's data insertion, which is integral to the CDC process.

- **Purpose**: Validates that new data entries are correctly inserted and detected by the CDC setup.
- **Function**: Includes `insert_data_to_mongodb` function to connect and insert data into MongoDB.
- **Usage**: It connects to MongoDB using a specified URI, inserts test data into a defined database and collection, and handles exceptions.
- **Testing Data**: Utilizes test data to simulate real insertion operations, aiding in verifying the overall functionality of the CDC system.

The script ensures that the CDC pipeline correctly interacts with MongoDB, acting as a part of the testing suite for the system.

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
- `make local-start`: Builds and starts MongoDB and RabbitMQ using Docker. This prepares the necessary services for the CDC system.
- `make local-start-cdc`: Starts the CDC system by running the `cdc.py` script.
- `make local-test-cdc`: Runs the `test_cdc.py` script to insert test data into MongoDB, testing the CDC system's response.

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
