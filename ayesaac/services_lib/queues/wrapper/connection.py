"""
connection.py
This file contains Connection class which is a wrapping of pika connection.
"""


from pika import BlockingConnection, ConnectionParameters


class Connection:
    def __init__(self, **kwargs):
        self.connection = BlockingConnection(ConnectionParameters(**kwargs))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=5)

    def __del__(self):
        self.connection.close()

    def start_consuming(self):
        self.channel.start_consuming()

    def stop_consuming(self):
        self.channel.stop_consuming()

    def get_channel(self):
        return self.channel

    def close(self):
        self.connection.close()
