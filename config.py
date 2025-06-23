import logging

import pika

MQ_HOST = "localhost"
MQ_PORT = 5672

MQ_USER = "admin"
MQ_PASSWORD = "admin"

MQ_EXCHANGE = ""
MQ_ROUTING_KEY = "test"

mq_connection_creds = pika.PlainCredentials(MQ_USER, MQ_PASSWORD)

mq_connection_params = pika.ConnectionParameters(
    host=MQ_HOST,
    port=MQ_PORT,
    credentials=mq_connection_creds,
)


def get_mq_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(mq_connection_params)


def configure_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s",
    )
