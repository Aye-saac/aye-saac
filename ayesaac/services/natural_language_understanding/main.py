from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager
import logging

logger = logging.getLogger(__name__)

from rasa.nlu.model import Interpreter
from os import listdir
from os.path import isdir, join

class NaturalLanguageUnderstanding(object):
    """
    The class NaturalLanguageUnderstanding purpose is to sense the objectives of the query.
    """
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Manager"])
        model_path = 'data/models/rasa/nlu'
        dirs = [f for f in listdir(model_path) if isdir(join(model_path, f))]
        pprint(dirs)
        dirs.sort(reverse=True)
        model = join(model_path, dirs[0])
        pprint(model)
        self.interpreter = Interpreter.load(model)

    def callback(self, body, **_):
        pprint(body)
        body['asking'] = body['query'].split()
        pprint(body['asking'])
        body['intents'] = self.interpreter.parse(body['query'])
        body['path_done'].append(self.__class__.__name__)
        pprint(body)
        self.queue_manager.publish('Manager', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_understanding = NaturalLanguageUnderstanding()
    natural_language_understanding.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filemode='w')
    main()