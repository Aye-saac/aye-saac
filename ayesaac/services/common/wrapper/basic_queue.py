"""
basic_queue.py

This file contains two class: CallBackWrapper and BasicQueue.
We choose pika (https://github.com/pika/pika) library base on RabbitMQ to create the
message queues, and we have wrap its usage in the case if we want to move from pika to
another library
"""


import json
from typing import Any, Callable

from .connection import Connection


class CallBackWrapper(object):
    """
    Wrap every services callback
    """

    def __init__(self, callback: Callable) -> None:
        self.callback = callback

    def __call__(self, chan, method_frame, header_frame, body) -> None:
        self.callback(
            ch=chan,
            method=method_frame,
            propriety=header_frame,
            body=json.loads(body.decode()),
        )
        chan.basic_ack(delivery_tag=method_frame.delivery_tag)


class BasicQueue(object):
    """
    Wrap basic queue
    """

    def __init__(
        self,
        connection: Connection,
        queue: str,
        consumer_tag: str = None,
        **kwargs: Any,
    ) -> None:
        self.queue = queue
        self.tag = consumer_tag
        self.channel = connection.get_channel()
        self.channel.queue_declare(queue=queue, **kwargs)

    def consuming(self, callback: Callable, **kwargs: Any) -> None:
        self.tag = self.channel.basic_consume(
            self.queue,
            on_message_callback=CallBackWrapper(callback),
            consumer_tag=self.tag,
            **kwargs,
        )

    def publish(self, body: str, **kwargs: Any) -> None:
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=json.dumps(body).encode(),
            **kwargs,
        )
