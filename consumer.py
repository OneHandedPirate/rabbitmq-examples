import logging
import random
import time
from typing import TYPE_CHECKING

from config import configure_logging, MQ_ROUTING_KEY
from rabbit import RabbitBase
from rabbit.common import SimpleRabbit

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
    logger.info("[ ] Start processing message: %r", body)
    start_time = time.time()

    number = int(body[-2:])
    is_odd = number % 2

    time.sleep(is_odd + 1)
    end_time = time.time()

    if method.delivery_tag is not None:
        if random.random() < 0.5:
            logger.info(
                "[+] Finished processing message %s in %.3fs. Sending ack",
                body,
                end_time - start_time,
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # logger.info(
            #     "[-] Could not process message %s in %.3fs. Rejected",
            #     body,
            #     end_time - start_time
            # )
            # channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
            logger.info(
                "[-] Could not process message %s in %.3fs. Sending nack (no requeue)",
                body,
                end_time - start_time,
            )
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            # logger.info(
            #     "[-] Could not process message %s in %.3fs. Sending nack",
            #     body,
            #     end_time - start_time,
            # )
            # channel.basic_nack(delivery_tag=method.delivery_tag)
    else:
        logger.warning("No delivery_tag found, message won't be acknowledged.")


def main():
    configure_logging()

    with SimpleRabbit() as rabbit:
        rabbit.consume_messages(message_callback=process_message)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
