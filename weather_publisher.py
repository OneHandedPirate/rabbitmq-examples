import logging
import time

from config import configure_logging
from rabbit.common import WeatherRabbit

logger = logging.getLogger(__name__)


class Published(WeatherRabbit):
    def produce_message(self, message: bytes) -> None:
        self.publish_message(message)


def main():
    configure_logging(logging.WARNING)
    with Published() as publisher:
        publisher.declare_queue()

        for idx in range(1, 3001):
            publisher.produce_message(
                bytes(
                    f"Weather report #{idx:04d} at {time.strftime('%H:%M:%S')}", "utf-8"
                )
            )
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
