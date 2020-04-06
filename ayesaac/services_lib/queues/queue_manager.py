"""
queue_manager.py
This file contains a class QueueManager, its job is to abstract the usage of the queue as simple as possible.
"""

import ayesaac.services_lib.queues.wrapper as queues


RABBITMQ_HOST = 'localhost'


class QueueManager:
    def __init__(self, queues_name):
        """
        :param queues_name: list of queues names which the service will access
        """
        self.connection = queues.Connection(host=RABBITMQ_HOST)
        self.queues = {}
        for queue_name in queues_name:
            self.queues[queue_name] = queues.BasicQueue(self.connection, queue_name)

    def publish(self, name, data):
        """
        send the data in the specify queue
        :param name: name of the queue
        :param data:
        """
        self.queues[name].publish(data)

    def start_consuming(self, name, callback):
        """
        start listening the queue for a message
        :param name: name of the queue to be listen
        :param callback: callback called when a message arrives
        """
        self.queues[name].consuming(callback)
        self.connection.start_consuming()
