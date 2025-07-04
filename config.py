import logging

import pika

MQ_HOST = "localhost"
MQ_PORT = 5672

MQ_USER = "admin"
MQ_PASSWORD = "admin"

MQ_EXCHANGE = ""
MQ_ROUTING_KEY = "test"

MQ_EMAIL_UPDATES_EXCHANGE_NAME = "email-updates"
MQ_QUEUE_NAME_KYC_EMAIL_UPDATES = "kyc-email-updates"
MQ_QUEUE_NAME_NEWSLETTER_EMAIL_UPDATES = "newsletter-email-updates"
MQ_SIMPLE_DEAD_LETTER_EXCHANGE_NAME = "simple-dead-letter"
MQ_SIMPLE_DEAD_LETTER_KEY = "dead-letter-key"

MQ_QUEUE_NAME_WEATHER_UPDATES = "q-weather-updates"
MQ_QUEUE_WEATHER_UPDATES_TTL = 60_000
MQ_WEATHER_DLQ_NAME = "q-expired-weather-updates"
MQ_QUEUE_WEATHER_EXPIRED_UPDATES_TTL = 120_000

MQ_EXCHANGE_PAINT_BUTTON_TASKS = "x-paint-button-tasks"
MQ_QUEUE_NAME_PAINT_BUTTON_TASKS = "q-paint-button-tasks"
MQ_DLX_NAME_FAILED_PAINT_BUTTON_TASKS = "dlx-failed-paint-button-tasks"
MQ_DLQ_NAME_FAILED_PAINT_BUTTON_TASKS = "dlq-failed-paint-button-tasks"
MQ_FAILED_TO_PAINT_BUTTON_TASKS_RETRY_TIME = 30  # retry time in seconds
MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS = "q-not-solved-paint-button-tasks"

LOG_FORMAT_FULL = "[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(funcName)20s %(levelname)-8s - %(message)s"
LOG_FORMAT_SHORT = "%(module)s:%(lineno)d %(levelname)-6s - %(message)s"

mq_connection_creds = pika.PlainCredentials(MQ_USER, MQ_PASSWORD)

mq_connection_params = pika.ConnectionParameters(
    host=MQ_HOST,
    port=MQ_PORT,
    credentials=mq_connection_creds,
)


def get_mq_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(mq_connection_params)


def configure_logging(
    level: int = logging.INFO,
    pika_log_level: int = logging.WARNING,
    short: bool = False,
) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=LOG_FORMAT_SHORT if short else LOG_FORMAT_FULL,
    )
    logging.getLogger("pika").setLevel(pika_log_level)
