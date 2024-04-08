import json
from streaming_pipeline.db.mongo import MongoDatabaseConnector
from streaming_pipeline.data_flow.mq import RabbitMQConnection


def stream_process():

    mq_connection = RabbitMQConnection()
    mq_connection.connect()

    client = MongoDatabaseConnector()
    db = client['scrabble']

    changes = db.watch([{
        '$match': {
            'operationType': {'$in': ['insert']}  # Filter for inserts only
        }
    }])
    for change in changes:
        data_type = change['ns']['coll']
        entry_id = change['fullDocument']['_id']
        change['fullDocument'].pop('_id')
        change['fullDocument']['type'] = data_type
        change['fullDocument']['entry_id'] = entry_id
        data = json.dumps(change['fullDocument'])

        mq_connection.publish_message(data=data, queue='mongo_data')


if __name__ == '__main__':
    stream_process()
