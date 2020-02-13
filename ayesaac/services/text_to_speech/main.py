
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager


class TextToSpeech(object):
    """
    The class TextToSpeech purpose is to deliver an audio from a given text.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__])

    def callback(self, body, **_):
        pprint(body)
        body['path_done'].append(self.__class__.__name__)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    text_to_speech = TextToSpeech()
    text_to_speech.run()


if __name__ == "__main__":
    main()
