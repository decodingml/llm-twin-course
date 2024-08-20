import json
import time
from datetime import datetime
from typing import Generic, Iterable, List, Optional, TypeVar

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition
from config import settings
from mq import RabbitMQConnection
from utils.logging import get_logger

logger = get_logger(__name__)

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")


class RabbitMQSource(FixedPartitionedSource, Generic[DataT, MessageT]):
    def list_parts(self) -> List[str]:
        return ["single partition"]

    def build_part(
        self, now: datetime, for_part: str, resume_state: MessageT | None = None
    ) -> StatefulSourcePartition[DataT, MessageT]:
        return RabbitMQPartition(queue_name=settings.RABBITMQ_QUEUE_NAME)


class RabbitMQPartition(StatefulSourcePartition, Generic[DataT, MessageT]):
    """
    Class responsible for creating a connection between bytewax and rabbitmq that facilitates the transfer of data from mq to bytewax streaming piepline.
    Inherits StatefulSourcePartition for snapshot functionality that enables saving the state of the queue
    """

    def __init__(self, queue_name: str, resume_state: MessageT | None = None) -> None:
        self._in_flight_msg_ids = resume_state or set()
        self.queue_name = queue_name
        self.connection = RabbitMQConnection()

        try:
            self.connection.connect()
            self.channel = self.connection.get_channel()
        except Exception:
            logger.warning(
                f"Error while trying to connect to the queue and get the current channel {self.queue_name}",
            )

    def next_batch(self, sched: Optional[datetime]) -> Iterable[DataT]:
        try:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.queue_name, auto_ack=True
            )
        except Exception:
            logger.warning(
                f"Error while fetching message from queue: {self.queue_name}", 
            )
            time.sleep(10)  # Sleep for 10 seconds before retrying to access the queue.

            self.connection.connect()
            self.channel = self.connection.get_channel()

            return []

        if method_frame:
            message_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(message_id)

            return [json.loads(body)]
        else:
            return []

    def snapshot(self) -> MessageT:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self):
        self.channel.close()
