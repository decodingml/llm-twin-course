import json
import logging

from bson import json_util
from config import settings
from db import MongoDatabaseConnector
from mq import publish_to_rabbitmq

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def stream_process():
    try:
        # Setup MongoDB connection
        client = MongoDatabaseConnector()
        db = client["scrabble"]
        logging.info("Connected to MongoDB.")

        # Watch changes in a specific collection
        changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])
        for change in changes:
            data_type = change["ns"]["coll"]
            entry_id = str(change["fullDocument"]["_id"])  # Convert ObjectId to string

            change["fullDocument"].pop("_id")
            change["fullDocument"]["type"] = data_type
            change["fullDocument"]["entry_id"] = entry_id

            if data_type not in ["articles", "posts", "repositories"]:
                logging.info(f"Unsupported data type: '{data_type}'")
                continue

            # Use json_util to serialize the document
            data = json.dumps(change["fullDocument"], default=json_util.default)
            logging.info(
                f"Change detected and serialized for a data sample of type {data_type}."
            )

            # Send data to rabbitmq
            publish_to_rabbitmq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=data)
            logging.info(f"Data of type '{data_type}' published to RabbitMQ.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    stream_process()
