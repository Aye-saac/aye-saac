
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager


class NaturalLanguageGenerator(object):
    """
    The class NaturalLanguageGenerator purpose is to translate the results obtain to a nicely phrase.
    """
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "TextToSpeech"])

    def callback(self, body, **_):
        pprint(body)

        response = 'I found '
        for result in body['results']:
            if body['results'][result] > 0:
                response += str(body['results'][result]) + ' '
                response += result + ' '
        response += '.'
        body["response"] = response
        pprint(body['response'])
        body["path_done"].append(self.__class__.__name__)

        del body["asking"], body["objects"], body["path"], body["query"], body["results"]
        self.queue_manager.publish("TextToSpeech", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_generator = NaturalLanguageGenerator()
    natural_language_generator.run()


if __name__ == "__main__":
    main()
