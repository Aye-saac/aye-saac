"""
queue_manager.py
This file contains a class QueueManager, its job is to abstract the usage of the queue
as simple as possible.
"""
from typing import Any, Callable, List

import pika

from ayesaac.utils.config import Config

from .wrapper.basic_queue import BasicQueue
from .wrapper.connection import Connection


config = Config()


class QueueManager(object):
    def __init__(self, queues_name: List[str]) -> None:
        """
        :param queues_name: list of queues names which the service will access
        """

        self.connection = self._create_connection()

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

    def _create_connection(self) -> Connection:
        host = config.rabbitmq.host

        if host != "localhost":
            # Don't use credentials for rabbitmq deployments on the same machine
            creds = pika.credentials.PlainCredentials(
                username=config.rabbitmq.username, password=config.rabbitmq.password
            )

            return Connection(host=host, credentials=creds)

        return Connection(host=host)
