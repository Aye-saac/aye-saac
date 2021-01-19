"""
connection.py
This file contains Connection class which is a wrapping of pika connection.
"""


from typing import Any

from pika import BlockingConnection, ConnectionParameters


class Connection(object):
    def __init__(self, **kwargs: Any) -> None:
        self.connection = BlockingConnection(ConnectionParameters(**kwargs))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=5)

    def __del__(self) -> None:
        self.connection.close()

    def start_consuming(self) -> None:
        self.channel.start_consuming()

    def stop_consuming(self) -> None:
        self.channel.stop_consuming()

    def get_channel(self):
        return self.channel

    def close(self) -> None:
        self.connection.close()
