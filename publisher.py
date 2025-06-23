import logging
import time
from typing import TYPE_CHECKING

from config import configure_logging, get_mq_connection, MQ_EXCHANGE, MQ_ROUTING_KEY

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

logger = logging.getLogger(__name__)


def declare_queue(
    channel: "BlockingChannel",
) -> None:
    channel.queue_declare(queue=MQ_ROUTING_KEY)
    logger.info("Declared queue: %s", MQ_ROUTING_KEY)


def produce_message(channel: "BlockingChannel", message: bytes) -> None:
    logger.info("Publishing message %s to %s. Time: %s", message, channel, time.time())
    channel.basic_publish(
        exchange=MQ_EXCHANGE,
        routing_key=MQ_ROUTING_KEY,
        body=message,
    )
    logger.info("Published message %s to %s", message, channel)


def main():
    configure_logging()
    with get_mq_connection() as mq_connection:
        logger.info("Created connection to MQ: %s", mq_connection)

        with mq_connection.channel() as channel:
            logger.info("Created channel %s", channel)
            declare_queue(channel)

            for idx in range(1, 11):
                produce_message(channel, bytes(f"Test message #{idx:02d}", "utf-8"))
                time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
