"""
queue_manager.py
This file contains a class QueueManager, its job is to abstract the usage of the queue
as simple as possible.
"""
import os
from typing import Any, Callable, List

import pika
from dotenv import find_dotenv, load_dotenv

from .wrapper.basic_queue import BasicQueue
from .wrapper.connection import Connection


load_dotenv(find_dotenv())

if "NONLOCAL_RABBITMQ" in os.environ:
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
else:
    RABBITMQ_HOST = "localhost"

rabbit_credentials = pika.credentials.PlainCredentials(
    username=os.getenv("RABBITMQ_USERNAME"),
    password=os.getenv("RABBITMQ_PASSWORD"),
)


class QueueManager(object):
    def __init__(self, queues_name: List[str]) -> None:
        """
        :param queues_name: list of queues names which the service will access
        """
        if RABBITMQ_HOST == "localhost":
            # Don't use credentials for rabbitmq deployments on the same machine
            self.connection = Connection(host=RABBITMQ_HOST)
        else:
            self.connection = Connection(
                host=RABBITMQ_HOST, credentials=rabbit_credentials
            )

        self.queues = {}
        for queue_name in queues_name:
            self.queues[queue_name] = BasicQueue(self.connection, queue_name)

    def publish(self, name: str, data: Any) -> None:
        """
        send the data in the specify queue
        :param name: name of the queue
        :param data:
        """
        self.queues[name].publish(data)

    def start_consuming(self, name: str, callback: Callable) -> None:
        """
        start listening the queue for a message
        :param name: name of the queue to be listen
        :param callback: callback called when a message arrives
        """
        self.queues[name].consuming(callback)
        self.connection.start_consuming()
