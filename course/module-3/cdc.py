import json

from bson import json_util
from data_flow.mq import RabbitMQConnection
from db.mongo import MongoDatabaseConnector


def stream_process() -> None:
    mq_connection = RabbitMQConnection()
    mq_connection.connect()

    client = MongoDatabaseConnector()

    db = client["scrabble"]

    changes = db.watch(
        [{"$match": {"operationType": {"$in": ["insert"]}}}]
    )  # Filter for inserts only
    for change in changes:
        data_type = change["ns"]["coll"]
        entry_id = str(change["fullDocument"]["_id"])

        change["fullDocument"].pop("_id")
        change["fullDocument"]["type"] = data_type
        change["fullDocument"]["entry_id"] = entry_id

        data = json.dumps(change["fullDocument"], default=json_util.default)
        mq_connection.publish_message(data=data, queue="mongo_data")


if __name__ == "__main__":
    stream_process()
