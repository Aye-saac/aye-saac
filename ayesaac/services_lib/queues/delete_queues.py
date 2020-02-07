"""
delete_queues.py
Usage:
     python3 delete_queues.py

Delete the RabbitMQ queues create by the services.
Can also be done by hand by accessing RabbitMQ in the browser 'http://localhost:15672/'.
"""

import pika


def delete_queues():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    queues_name = ["CameraManager", "Manager", "Interpreter", "ObjectDetection", "NaturalLanguageUnderstanding",
                   "NaturalLanguageGenerator", "AutomaticSpeechRecognition", "TextToSpeech"]
    for queue_name in queues_name:
        channel.queue_delete(queue=queue_name)


if __name__ == '__main__':
    delete_queues()
