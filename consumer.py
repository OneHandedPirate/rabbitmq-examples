import logging
import time
from typing import TYPE_CHECKING

from config import configure_logging, get_mq_connection, MQ_ROUTING_KEY

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


def process_message(
    channel: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
) -> None:
    logger.info("Channel: %s", channel)
    logger.info("Method: %s", method)
    logger.info("Properties: %s", properties)
    logger.info("Body: %s", body)

    logger.info("[ ] Start processing message: %r", body)
    start_time = time.time()

    number = int(body[-2:])
    is_odd = number % 2

    time.sleep(is_odd * 2 + 1)
    end_time = time.time()
    logger.info(
        "[X] Finished processing message %s in %.3fs", body, end_time - start_time
    )
    logger.info("Sending acknowledgement")
    channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_messages(channel: "BlockingChannel") -> None:
    channel.basic_consume(
        queue=MQ_ROUTING_KEY,
        on_message_callback=process_message,
        # auto_ack=True,  # auto acknowledgment
    )
    logger.info("Waiting for messages...")
    channel.start_consuming()


def main():
    configure_logging()
    with get_mq_connection() as mq_connection:
        logger.info("Created connection to MQ: %s", mq_connection)

        with mq_connection.channel() as channel:
            logger.info("Created channel %s", channel)
            channel.basic_qos(prefetch_count=1)
            consume_messages(channel)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
