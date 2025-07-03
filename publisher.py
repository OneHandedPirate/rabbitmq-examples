import logging
import time

from config import MQ_EXCHANGE, MQ_ROUTING_KEY, configure_logging
from rabbit.common import SimpleRabbit

logger = logging.getLogger(__name__)


class Published(SimpleRabbit):
    def produce_message(self, message: bytes) -> None:
        logger.info(
            "Publishing message %s to %s. Time: %s", message, self.channel, time.time()
        )
        self.channel.basic_publish(
            exchange=MQ_EXCHANGE,
            routing_key=MQ_ROUTING_KEY,
            body=message,
        )
        logger.warning("Published message %s", message)


def main():
    configure_logging(logging.WARNING)
    with Published() as publisher:
        publisher.declare_queue()

        for idx in range(1, 11):
            publisher.produce_message(bytes(f"Test message #{idx:02d}", "utf-8"))
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
