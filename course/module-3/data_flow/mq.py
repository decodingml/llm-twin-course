import pika

from streaming_pipeline.settings import settings
from pika import exceptions


class RabbitMQConnection:
    _instance = None

    def __new__(
            cls,
            host: str = None,
            port: int = None,
            username: str = None,
            password: str = None,
            virtual_host: str = '/'
    ):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            host: str = None,
            port: int = None,
            username: str = None,
            password: str = None,
            virtual_host: str = '/',
            fail_silently: bool = False,
            **kwargs
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

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=credentials
                ))
        except pika.exceptions.AMQPConnectionError as e:
            print("Failed to connect to RabbitMQ:", e)
            if not self.fail_silently:
                raise e

    def publish_message(self, data, queue):
        channel = self.get_channel()
        channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
        channel.confirm_delivery()

        try:
            channel.basic_publish(exchange='',
                                  routing_key='mongo_data',
                                  body=data,
                                  mandatory=True)
            print('sent changes to RabbitMQ:', data)
        except pika.exceptions.UnroutableError:
            print('Message could not be confirmed')

    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_open

    def get_channel(self):
        if self.is_connected():
            return self._connection.channel()

    def close(self):
        if self.is_connected():
            self._connection.close()
            self._connection = None
            print("Closed RabbitMQ connection")
