import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from pika.exchange_type import ExchangeType

from config import MQ_EMAIL_UPDATES_EXCHANGE_NAME
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class RabbitEmailsMixin:
    channel: "BlockingChannel"

    def declare_email_updates_exchange(self) -> None:
        self.channel.exchange_declare(
            exchange=MQ_EMAIL_UPDATES_EXCHANGE_NAME,
            exchange_type=ExchangeType.fanout,
        )

    def declare_email_updates_queue(
        self,
        queue_name: str = "",
        exclusive: bool = True,
    ) -> str:
        self.declare_email_updates_exchange()
        queue = self.channel.queue_declare(
            queue=queue_name,
            exclusive=exclusive,
        )

        q_name = queue.method.queue

        self.channel.queue_bind(
            exchange=MQ_EMAIL_UPDATES_EXCHANGE_NAME,
            queue=q_name,
        )

        return q_name

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
        queue_name: str = "",
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        q_name = self.declare_email_updates_queue(
            queue_name=queue_name, exclusive=not queue_name
        )
        self.channel.basic_consume(
            queue=q_name,
            on_message_callback=message_callback,
        )
        logger.info("Waiting for messages...")
        self.channel.start_consuming()


class EmailUpdatesRabbit(RabbitEmailsMixin, RabbitBase): ...
