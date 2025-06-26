import logging
from typing import TYPE_CHECKING, Callable

from pika.exchange_type import ExchangeType

from config import (
    MQ_ROUTING_KEY,
    MQ_SIMPLE_DEAD_LETTER_KEY,
    MQ_SIMPLE_DEAD_LETTER_EXCHANGE_NAME,
)
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class SimpleRabbitMixin:
    channel: "BlockingChannel"

    def declare_queue(self) -> None:
        self.channel.exchange_declare(
            exchange=MQ_SIMPLE_DEAD_LETTER_EXCHANGE_NAME,
            exchange_type=ExchangeType.fanout,
        )
        dlq = self.channel.queue_declare(
            queue=MQ_SIMPLE_DEAD_LETTER_KEY,
        )
        self.channel.queue_bind(
            exchange=MQ_SIMPLE_DEAD_LETTER_EXCHANGE_NAME,
            queue=MQ_SIMPLE_DEAD_LETTER_KEY,
        )
        logger.info("Declared dlq: %s", dlq.method.queue)
        queue = self.channel.queue_declare(
            queue=MQ_ROUTING_KEY,
            arguments={
                "x-dead-letter-exchange": MQ_SIMPLE_DEAD_LETTER_EXCHANGE_NAME,
            },
        )
        logger.info("Declared queue: %s", queue.method.queue)

    def consume_messages(
        self,
        message_callback: Callable[
            [
                "BlockingChannel",
                "Basic.Deliver",
                "BasicProperties",
                bytes,
            ],
            None,
        ],
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=MQ_ROUTING_KEY,
            on_message_callback=message_callback,
            # auto_ack=True,  # auto acknowledgment
        )
        logger.info("Waiting for messages...")
        self.channel.start_consuming()


class SimpleRabbit(SimpleRabbitMixin, RabbitBase): ...
