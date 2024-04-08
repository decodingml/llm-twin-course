import json

from datetime import datetime
from typing import Iterable, Optional, TypeVar, List
from bytewax.inputs import StatefulSourcePartition, FixedPartitionedSource
from streaming_pipeline.data_flow.mq import RabbitMQConnection

DATA = TypeVar('DATA')  # The type of the items being produced in this case the data from the queue.
MESSAGE_ID = TypeVar('MESSAGE_ID')  # The type of the state being saved and resumed in this case last message id from Rabbitmq.


class RabbitMQPartition(StatefulSourcePartition):
    """
    Class responsible for creating a connection between bytewax and rabbitmq that facilitates the transfer of data from mq to bytewax streaming piepline.
    Inherits StatefulSourcePartition for snapshot functionality that enables saving the state of the queue
    """

    def __init__(self, queue_name, resume_state=None):
        self._in_flight_msg_ids = resume_state or set()
        self.queue_name = queue_name
        self.connection = RabbitMQConnection()
        self.connection.connect()
        self.channel = self.connection.get_channel()

    def next_batch(self, sched: Optional[datetime]) -> Iterable[DATA]:
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=False)
        if method_frame:
            message_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(message_id)
            return [json.loads(body)]
        else:
            return []

    def snapshot(self) -> MESSAGE_ID:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self):
        self.channel.close()


class RabbitMQSource(FixedPartitionedSource):

    def list_parts(self) -> List[str]:
        return ['single partition']

    def build_part(self, now: datetime, for_part: str, resume_state: Optional[MESSAGE_ID]) -> StatefulSourcePartition[DATA, MESSAGE_ID]:
        return RabbitMQPartition(queue_name='mongo_data')
