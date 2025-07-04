import logging
import time

from config import configure_logging
from rabbit.common import PaintButtonRabbit

logger = logging.getLogger(__name__)


class Published(PaintButtonRabbit):
    def produce_message(self, message: bytes) -> None:
        self.publish_message(message)


def main():
    configure_logging(logging.WARNING)
    with Published() as publisher:
        publisher.declare_queue()

        for idx in range(1, 33):
            publisher.produce_message(bytes(f"Paint button task #{idx:02d}", "utf-8"))
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye!")
