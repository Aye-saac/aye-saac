import copy
import time
from pprint import pprint
from secrets import token_hex

from ayesaac.services.common import QueueManager
from ayesaac.utils.logger import get_logger


logger = get_logger(__file__)


class Manager(object):
    """
    The class Manager purpose is to create a path inside the dialogue manager depending on the goal of the query.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "CameraManager"])
        # TODO: Missing intent for lateral position
        self.intents_to_path = {
            "read_text": [["CameraManager", "OCR", "LabelFormatter", "Interpreter"]],
            "detect_colour": [
                ["CameraManager", "ObjectDetection", "ColourDetection", "Interpreter"]
            ],
            "identify": [
                ["CameraManager", "OCR", "Interpreter"],
                ["CameraManager", "ObjectDetection", "Interpreter"],
            ],
            "recognise": [["CameraManager", "ObjectDetection", "Interpreter"]],
            "locate": [["CameraManager", "ObjectDetection", "Interpreter"]],
        }

        logger.info(f"{self.__class__.__name__} ready")

    def callback(self, body, **_):
        intern_token = token_hex(8)
        intent = body["intents"]["intent_ranking"][0]["name"]
        body["intern_token"] = intern_token
        body["wait_package"] = (
            len(self.intents_to_path[intent]) if intent in self.intents_to_path else 0
        )
        body["path_done"].append(self.__class__.__name__)

        intents_path = (
            copy.deepcopy(self.intents_to_path[intent])
            if intent in self.intents_to_path
            else []
        )

        for path in intents_path:
            pprint(path)

            body_ = copy.deepcopy(body)
            body_["vision_path"] = path
            next_service = body_["vision_path"].pop(0)
            self.queue_manager.publish(next_service, body_)
            if "run_as_webservice" not in body:
                time.sleep(1)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    manager = Manager()
    manager.run()


if __name__ == "__main__":
    main()
