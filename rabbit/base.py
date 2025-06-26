from typing import Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel

import config
from rabbit.exc import RabbitException


class RabbitBase:
    def __init__(
        self, connection_params: pika.ConnectionParameters = config.mq_connection_params
    ) -> None:
        self.connection_params = connection_params
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

    def get_connection(self) -> pika.BlockingConnection:
        if self._connection is None:
            self._connection = pika.BlockingConnection(self.connection_params)
        return self._connection

    @property
    def channel(self) -> BlockingChannel:
        if self._channel is None:
            raise RabbitException("You should you context manager")
        return self._channel

    def __enter__(self) -> "RabbitBase":
        self.get_connection()
        self._channel = self._connection.channel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._channel.is_open:
            self._channel.close()
        if self._connection.is_open:
            self._connection.close()
