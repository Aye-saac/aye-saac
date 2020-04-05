"""
queue_manager.py
This file contains a class QueueManager, its job is to abstract the usage of the queue as simple as possible.
"""
import pika

import ayesaac.services_lib.queues.wrapper as queues


RABBITMQ_HOST = 'rabbitmq'

# todo use actual creds from environment
# rabbit_credentials = pika.credentials.PlainCredentials(username='test-user', password='test-user')
rabbit_credentials = pika.credentials.PlainCredentials(username='user', password='bitnami')


class QueueManager:
    def __init__(self, queues_name):
        """
        :param queues_name: list of queues names which the service will access
        """
        self.connection = queues.Connection(host=RABBITMQ_HOST, credentials=rabbit_credentials)
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
