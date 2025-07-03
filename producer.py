import logging
import time

from config import MQ_EMAIL_UPDATES_EXCHANGE_NAME, configure_logging
from rabbit.common import EmailUpdatesRabbit

logger = logging.getLogger(__name__)


class Producer(EmailUpdatesRabbit):
    def produce_message(self, message: bytes) -> None:
        logger.info(
            "Publishing message %s to %s. Time: %s", message, self.channel, time.time()
        )
        self.channel.basic_publish(
            exchange=MQ_EMAIL_UPDATES_EXCHANGE_NAME,
            routing_key="",
            body=message,
        )
        logger.info("Published message %s to %s", message, self.channel)


def main():
    configure_logging()
    with Producer() as producer:
        producer.declare_email_updates_exchange()
        for idx in range(1, 10):
            producer.produce_message(bytes(f"New message #{idx:02d}", "utf-8"))
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
