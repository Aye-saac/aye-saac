
from pprint import pprint

from lib.queues.queue_manager import QueueManager


class Manager(object):
    """
    The class Manager purpose is to create a path inside the dialogue manager depending on the goal of the query.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "CameraManager"])

    def callback(self, body, **_):
        pprint(body)
        body['path'] = ['ObjectDetection']
        pprint(body['path'])
        body["path_done"].append(self.__class__.__name__)
        self.queue_manager.publish("CameraManager", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    manager = Manager()
    manager.run()


if __name__ == "__main__":
    main()
