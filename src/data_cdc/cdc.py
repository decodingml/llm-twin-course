import json
import logging

from bson import json_util
from config import settings
from core.db.mongo import MongoDatabaseConnector
from core.logger_utils import get_logger
from core.mq import publish_to_rabbitmq

logger = get_logger(__file__)


def stream_process():
    try:
        client = MongoDatabaseConnector()
        db = client["twin"]
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
            logger.info(
                f"Change detected and serialized for a data sample of type {data_type}."
            )

            # Send data to rabbitmq
            publish_to_rabbitmq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=data)
            logger.info(f"Data of type '{data_type}' published to RabbitMQ.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    stream_process()
