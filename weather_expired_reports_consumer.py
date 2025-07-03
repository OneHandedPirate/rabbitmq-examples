import logging
import time
from typing import TYPE_CHECKING

from config import MQ_WEATHER_DLQ_NAME, configure_logging
from rabbit.common import WeatherRabbit

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


def process_new_weather_report(
    channel: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
) -> None:
    logger.info("[ ] Start processing expired weather report: %r", body)
    time.sleep(2)
    if method.delivery_tag is not None:
        logger.info(
            "[+] Finished processing expired weather report %s. Sending ack",
            body,
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    configure_logging()

    with WeatherRabbit() as rabbit:
        rabbit.consume_messages(
            message_callback=process_new_weather_report, queue_name=MQ_WEATHER_DLQ_NAME
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
