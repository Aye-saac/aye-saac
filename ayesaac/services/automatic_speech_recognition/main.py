
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager


class AutomaticSpeechRecognition(object):
    """
    The class AutomaticSpeechRecognition purpose is to convert speech to text.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "NaturalLanguageUnderstanding"])

    def callback(self, body, **_):
        pprint(body)
        if 'query' not in body:
            body["query"] = "Is there a person in the kitchen ?"
        pprint(body["query"])
        body["path_done"].append(self.__class__.__name__)
        self.queue_manager.publish("NaturalLanguageUnderstanding", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    automatic_speech_recognition = AutomaticSpeechRecognition()
    automatic_speech_recognition.run()


if __name__ == "__main__":
    main()
