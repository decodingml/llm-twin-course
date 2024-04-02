import json

from data_flow.mq import publish_to_rabbitmq
from db.mongo import MongoDatabaseConnector


def stream_process():
    # Setup MongoDB connection
    client = MongoDatabaseConnector()
    db = client["scrabble"]

    # Watch changes in a specific collection
    changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])
    for change in changes:
        data_type = change["ns"]["coll"]
        entry_id = change["fullDocument"]["_id"]
        change["fullDocument"].pop("_id")
        change["fullDocument"]["type"] = data_type
        change["fullDocument"]["entry_id"] = entry_id
        data = json.dumps(change["fullDocument"])
        # Send data to rabbitmq
        publish_to_rabbitmq(data=data)


if __name__ == "__main__":
    stream_process()
