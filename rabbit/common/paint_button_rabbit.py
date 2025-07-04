import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from pika.exchange_type import ExchangeType

from config import (
    MQ_DLQ_NAME_FAILED_PAINT_BUTTON_TASKS,
    MQ_DLX_NAME_FAILED_PAINT_BUTTON_TASKS,
    MQ_EXCHANGE_PAINT_BUTTON_TASKS,
    MQ_FAILED_TO_PAINT_BUTTON_TASKS_RETRY_TIME,
    MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS,
    MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
)
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class PaintButtonRabbitMixin:
    channel: "BlockingChannel"

    def publish_message(
        self,
        body: bytes,
        exchange: str = MQ_EXCHANGE_PAINT_BUTTON_TASKS,
        routing_key: str = MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
    ) -> None:
        logger.info("Publishing message %s", body)
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
        )
        logger.warning("Published message %s", body)

    def declare_dlq(self) -> str:
        self.channel.exchange_declare(
            exchange=MQ_DLX_NAME_FAILED_PAINT_BUTTON_TASKS,
            exchange_type=ExchangeType.fanout,
        )

        dlq = self.channel.queue_declare(
            queue=MQ_DLQ_NAME_FAILED_PAINT_BUTTON_TASKS,
            arguments={
                "x-message-ttl": MQ_FAILED_TO_PAINT_BUTTON_TASKS_RETRY_TIME * 1000,
                "x-dead-letter-exchange": MQ_EXCHANGE_PAINT_BUTTON_TASKS,
                "x-dead-letter-routing-key": MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
            },
        )
        self.channel.queue_bind(
            queue=dlq.method.queue, exchange=MQ_DLX_NAME_FAILED_PAINT_BUTTON_TASKS
        )
        logger.info("Declared paint button dlq %r", dlq.method.queue)

        return dlq.method.queue

    def declare_main_queue(self) -> str:
        self.channel.exchange_declare(
            exchange=MQ_EXCHANGE_PAINT_BUTTON_TASKS,
            exchange_type=ExchangeType.direct,
        )
        main_queue = self.channel.queue_declare(
            queue=MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
            arguments={
                "x-dead-letter-exchange": MQ_DLX_NAME_FAILED_PAINT_BUTTON_TASKS,
            },
        )
        self.channel.queue_bind(
            queue=main_queue.method.queue,
            exchange=MQ_EXCHANGE_PAINT_BUTTON_TASKS,
        )
        logger.info("Declared paint button tasks queue %r", main_queue.method.queue)
        return main_queue.method.queue

    def declare_last_resort_queue(self) -> str:
        queue = self.channel.queue_declare(
            queue=MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS
        )
        logger.info("Declared last resort queue %r", queue.method.queue)

        return queue.method.queue

    def declare_queue(self) -> None:
        self.declare_last_resort_queue()
        self.declare_dlq()
        self.declare_main_queue()

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
        queue_name: str = MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_callback,
            # auto_ack=True,  # auto acknowledgment
        )
        logger.info("Waiting for paint button tasks...")
        self.channel.start_consuming()


class PaintButtonRabbit(PaintButtonRabbitMixin, RabbitBase): ...
