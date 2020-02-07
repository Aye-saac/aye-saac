
from pprint import pprint

from lib.queues.queue_manager import QueueManager


class Interpreter(object):
    """
    The Interpreter class purpose is a simple comparison with what the vision part find out and what the user asked for.
    (Which object was found and not found)
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, 'NaturalLanguageGenerator'])

    def callback(self, body, **_):
        pprint(body)

        objects_asked = body['asking']
        objects_found = body['objects']
        results = {}
        for object_asked in objects_asked:
            results[object_asked] = 0
        for object_found in objects_found:
            if (object_found['name'] in objects_asked or '*' in objects_asked) and object_found['confidence'] > 0.5:
                results[object_found['name']] += 1

        body["results"] = results
        pprint(body["results"])
        body["path_done"].append(self.__class__.__name__)
        self.queue_manager.publish('NaturalLanguageGenerator', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    interpreter = Interpreter()
    interpreter.run()


if __name__ == "__main__":
    main()
