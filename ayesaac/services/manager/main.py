from pprint import pprint
from secrets import token_hex
from ayesaac.services_lib.queues.queue_manager import QueueManager


class Manager(object):
    """
    The class Manager purpose is to create a path inside the dialogue manager depending on the goal of the query.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "CameraManager"])
        # TODO: Missing intent for lateral position
        self.intents_to_path = {
            "read_text": [["OCR", "Interpreter"]],
            "detect_color": [["ObjectDetection", "ColorDetection", "Interpreter"]],
            "identify": [["OCR", "Interpreter"], ["ObjectDetection", "Interpreter"]],
            "recognise": [["ObjectDetection", "Interpreter"]],
        }

    def callback(self, body, **_):
        intern_token = token_hex(8)
        intent = body["intents"]["intent_ranking"][0]["name"]
        body["intern_token"] = intern_token
        body["wait_package"] = len(self.intents_to_path[intent])
        body["vision_path"] = self.intents_to_path[intent]
        pprint(body)
        body["path_done"].append(self.__class__.__name__)
        self.queue_manager.publish("CameraManager", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    manager = Manager()
    manager.run()


if __name__ == "__main__":
    main()
