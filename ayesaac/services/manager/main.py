
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager


class Manager(object):
    """
    The class Manager purpose is to create a path inside the dialogue manager depending on the goal of the query.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "CameraManager"])
        # TODO: It missing an intent for the position
        self.intents_to_path = {'read_text': ['OCR', 'Interpreter'],
                                'detect_color': ['ObjectDetection', 'ColorDetection', 'Interpreter'],
                                'identify': ['ObjectDetection', 'Interpreter'],
                                'recognize': ['ObjectDetection', 'Interpreter'],
                                }

    def callback(self, body, **_):
        intent = body['intents']['intent_ranking'][0]['name']
        body['vision_path'] = self.intents_to_path[intent]
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
