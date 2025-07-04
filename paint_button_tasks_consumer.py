import logging
import random
import time
from typing import TYPE_CHECKING, Optional

from config import (
    MQ_EXCHANGE,
    MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS,
    configure_logging,
)
from rabbit.common import PaintButtonRabbit

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


def can_solve() -> bool:
    return random.random() < 0.2


def extract_deaths_count(
    headers: Optional[dict[str, list[dict[str, int | str]]]],
) -> int:
    if headers and headers.get("x-death"):
        for props in headers["x-death"]:
            if "count" in props:
                return int(props["count"])
    return 0


def process_paint_button_task(
    channel: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
) -> None:
    deaths_count = extract_deaths_count(properties.headers)

    logger.info(
        "[ ] Start processing paint button task: %r. Deaths: %d", body, deaths_count
    )
    time.sleep(0.5)
    if method.delivery_tag is not None:
        if can_solve():
            logger.info(
                "[+] Finished processing paint button task %s after %d retries. Sending ack",
                body,
                deaths_count,
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        if deaths_count < 5:
            logger.info(
                "[-] Failed processing paint button task report %s. Rejected",
            )
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        logger.info("[X] Delay task after %d retries.", deaths_count)
        channel.basic_publish(
            exchange=MQ_EXCHANGE,
            routing_key=MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS,
            properties=properties,
            body=body,
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    configure_logging(short=True)

    with PaintButtonRabbit() as rabbit:
        rabbit.consume_messages(message_callback=process_paint_button_task)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
