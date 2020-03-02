
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager

from rasa.nlu.model import Interpreter
from os import listdir
from os.path import isdir, join

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

        model_path = 'data/models/rasa/nlu'

        try:
            dirs = [f for f in listdir(model_path) if isdir(join(model_path, f))]
            pprint(dirs)

            dirs.sort(reverse=True)
            try:
                model = join(model_path, dirs[0])
                pprint(model)
                try:
                    interpreter = Interpreter.load(model)
                    body['intents'] = interpreter.parse(body['query'])
                except:
                    pprint("An unexpected error occured.")
            except IndexError:
                pprint("Index out of range. The given directory '" + model_path + "' is empty. Please ensure there is at least one model directory.")
        except IOError:
            pprint("Could not access given directory '" + model_path + "'. Please verify rights.")

        body['path_done'].append(self.__class__.__name__)
        self.queue_manager.publish('Manager', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_understanding = NaturalLanguageUnderstanding()
    natural_language_understanding.run()


if __name__ == "__main__":
    main()