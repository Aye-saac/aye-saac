from os import listdir
from os.path import isdir, join

from rasa.nlu.model import Interpreter

from ayesaac.services.common import QueueManager
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger


config = Config()

logger = get_logger(__file__)


def contains_word(s, w):
    """
    Checks whether a string contains a certain word
    """
    return f" {w} " in f" {s} "


def contains_at_least_one_word(s, arr):
    """
    Checks whether a string contains at least one word coming from an array of words
    """

    for elem in arr:
        if contains_word(s, elem):
            return True
    return False


def check_followup(query):
    """
    Checks whether the query is a followup query and returns if we should add the last
    entities found to the current query.
    """
    if contains_at_least_one_word(
        query, ["it", "that", "this", "them", "they", "those", "these"]
    ):
        return True
    return False


class NaturalLanguageUnderstanding(object):
    """
    The class NaturalLanguageUnderstanding purpose is to sense the objectives of the
    query.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Manager"])
        self.previous_query = None

        model_path = str(config.directory.data.joinpath("rasa", "nlu"))

        dirs = [f for f in listdir(model_path) if isdir(join(model_path, f))]
        dirs.sort(reverse=True)
        model = join(model_path, dirs[0])
        self.interpreter = Interpreter.load(model)

        logger.info(f"{self.__class__.__name__} ready")

    def callback(self, body, **_):
        body["asking"] = body["query"].split()
        intents = self.interpreter.parse(body["query"])
        try:
            if (
                intents["intent"]["name"] == "same_intent"
                and self.previous_query != None
            ):
                intents["intent"]["name"] = self.previous_query["intent"]["name"]
            if (
                intents["intent"]["name"] != "recognise"
                and intents["intent"]["name"] != "identify"
                and check_followup(body["query"]) == True
            ):
                intents["entities"].extend(self.previous_query["entities"])
        except IndexError as error:
            logger.error(error)
        except Exception as exception:
            logger.warning(exception)
        self.previous_query = intents
        body["intents"] = intents
        body["path_done"].append(self.__class__.__name__)
        # logger.info(body)

        self.queue_manager.publish("Manager", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_understanding = NaturalLanguageUnderstanding()
    natural_language_understanding.run()


if __name__ == "__main__":

    main()
