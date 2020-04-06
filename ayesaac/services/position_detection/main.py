
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager

import os
from random import choice

class PositionDetection(object):
    """
    The class PositionDetection purpose provide the global position of the detected objects.
    """
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

    def get_pos_str(self, obj, max_pos=(1, 1)):
        step = (max_pos[0]/3, max_pos[1]/3)
        center = ((obj['bbox'][0]+obj['bbox'][2])/2, (obj['bbox'][1]+obj['bbox'][3])/2)
        if center[1]>2*step[1]:
            return ' on the left'
        elif center[1]>step[1]:
            return ' in the center'
        return ' on the right'

    def callback(self, body, **_):
        pprint(body)

        for i, obj in enumerate(body['objects']):
            body['objects'][i]['lateral_position'] = self.get_pos_str(obj)

        body["path_done"].append(self.__class__.__name__)
        next_service = body['vision_path'].pop(0)
        self.queue_manager.publish(next_service, body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    position_detection = PositionDetection()
    position_detection.run()


if __name__ == "__main__":
    main()
