import pika

from utils.logging import get_logger
from config import settings

logger = get_logger(__name__)


class RabbitMQConnection:
    _instance = None

    def __new__(
        cls,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str = "/",
    ):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str = "/",
        fail_silently: bool = False,
        **kwargs,
    ):
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self) -> None:
        logger.info("Trying to connect to RabbitMQ.", host=self.host, port=self.port)
        
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=credentials,
                )
            )
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning("Failed to connect to RabbitMQ.")

            if not self.fail_silently:
                raise e

    def publish_message(self, data: str, queue: str):
        channel = self.get_channel()
        channel.queue_declare(
            queue=queue, durable=True, exclusive=False, auto_delete=False
        )
        channel.confirm_delivery()

        try:
            channel.basic_publish(
                exchange="", routing_key=queue, body=data, mandatory=True
            )
            logger.info(
                "Sent message successfully.", queue_type="RabbitMQ", queue_name=queue
            )
        except pika.exceptions.UnroutableError:
            logger.info(
                "Failed to send the message.", queue_type="RabbitMQ", queue_name=queue
            )

    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_open

    def get_channel(self):
        if self.is_connected():
            return self._connection.channel()

    def close(self):
        if self.is_connected():
            self._connection.close()
            self._connection = None

            logger.info("Closed RabbitMQ connection.")
