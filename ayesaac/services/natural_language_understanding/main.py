
from pprint import pprint

from lib.queues.queue_manager import QueueManager


class NaturalLanguageUnderstanding(object):
    """
    The class NaturalLanguageUnderstanding purpose is to sense the objectives of the query.
    """
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Manager"])

    def callback(self, body, **_):
        pprint(body)
        body['asking'] = body['query'].split()
        pprint(body['asking'])
        body['path_done'].append(self.__class__.__name__)
        self.queue_manager.publish('Manager', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_understanding = NaturalLanguageUnderstanding()
    natural_language_understanding.run()


if __name__ == "__main__":
    main()