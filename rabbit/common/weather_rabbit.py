import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from config import (
    MQ_EXCHANGE,
    MQ_QUEUE_NAME_WEATHER_UPDATES,
    MQ_QUEUE_WEATHER_EXPIRED_UPDATES_TTL,
    MQ_QUEUE_WEATHER_UPDATES_TTL,
    MQ_WEATHER_DLQ_NAME,
)
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class WeatherRabbitMixin:
    channel: "BlockingChannel"

    def publish_message(
        self, body: bytes, routing_key: str = MQ_QUEUE_NAME_WEATHER_UPDATES
    ) -> None:
        logger.info("Publishing message %s", body)
        self.channel.basic_publish(
            exchange=MQ_EXCHANGE,
            routing_key=routing_key,
            body=body,
        )
        logger.warning("Published message %s", body)

    def declare_queue(self) -> None:
        dlq = self.channel.queue_declare(
            queue=MQ_WEATHER_DLQ_NAME,
            arguments={"x-message-ttl": MQ_QUEUE_WEATHER_EXPIRED_UPDATES_TTL},
        )
        logger.info("Declared weather dlq %r", dlq.method.queue)
        weather_queue = self.channel.queue_declare(
            queue=MQ_QUEUE_NAME_WEATHER_UPDATES,
            arguments={
                "x-message-ttl": MQ_QUEUE_WEATHER_UPDATES_TTL,
                "x-dead-letter-exchange": MQ_EXCHANGE,
                "x-dead-letter-routing-key": MQ_WEATHER_DLQ_NAME,
            },
        )
        logger.info("Declared weather queue %r", weather_queue.method.queue)

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
        queue_name: str = MQ_QUEUE_NAME_WEATHER_UPDATES,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_callback,
            # auto_ack=True,  # auto acknowledgment
        )
        logger.info("Waiting for messages...")
        self.channel.start_consuming()


class WeatherRabbit(WeatherRabbitMixin, RabbitBase): ...
