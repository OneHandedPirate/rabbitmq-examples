import logging
import time
from typing import TYPE_CHECKING

from config import MQ_QUEUE_NAME_NEWSLETTER_EMAIL_UPDATES, configure_logging
from rabbit.common import EmailUpdatesRabbit

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

    logger.info("[ ] Start new email user updates: %r", body)

    start_time = time.time()
    time.sleep(1)
    end_time = time.time()
    logger.info(
        "[X] User email successfully updated %s in %.3fs. Message is ok",
        body,
        end_time - start_time,
    )
    logger.info("Sending acknowledgement")
    if method.delivery_tag is not None:
        channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        logger.warning("No delivery_tag found, message won't be acknowledged.")


def main():
    """
    - declare exchange
    - bind queue
    - start consuming messages
    :return:
    """

    configure_logging()

    with EmailUpdatesRabbit() as rabbit:
        rabbit.consume_messages(
            message_callback=process_message,
            queue_name=MQ_QUEUE_NAME_NEWSLETTER_EMAIL_UPDATES,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
