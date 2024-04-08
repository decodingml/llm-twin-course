# Module 2: Change Data Capture: Enabling Event-Driven Architectures


## Introduction
Change Data Capture, commonly known as CDC, is an efficient way to track changes in a database.

The purpose of CDC is to capture insertions, updates, and deletions applied to a database and to make this change data available in a format easily consumable by downstream applications.
Why do we need CDC pattern?

    1. Real-time Data Syncing: CDC facilitates near-real-time data integration and syncing.
    2. Efficient Data Pipelines: It allows incremental data loading, which is more efficient than bulk load operations.
    3. Minimized System Impact: CDC minimizes the impact on the source system by reducing the need for performance-intensive queries.
    4. Event-Driven Architectures: It enables event-driven architectures by streaming database events.


## Contents
- data_flow module:  Singleton class to manage RabbitMQ connection.
    - mq.py
- db module: Singleton class to connect to MongoDB database.
    - mongo.py
- cdc.py :
- **Functionality**: This script sets up a CDC pipeline. It monitors a MongoDB database for changes and forwards these changes to a RabbitMQ message queue.
- **MongoDB Connection**: It connects to a MongoDB database (specifically the "scrabble" collection), utilizing a class from `db.mongo`.
- **Change Tracking**: The script watches for insert operations in MongoDB. When a change is detected, it processes and serializes the change details.
- **Data Processing**: Each change's metadata is extracted and serialized using `json_util`. The `_id` field is converted to a string and additional metadata is added.
- **RabbitMQ Integration**: After serialization, the script publishes the data to a RabbitMQ queue named "test_queue".
- test_cdc.py