
import cv2
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager
from services_lib.images.crypter import encode


class CameraManager(object):
    """
    The class CameraManager goal is to organise the collect of pictures from different camera sources.
    For the time being it is considered as a simple camera, in this case, the webcam.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, 'ObjectDetection'])

    def callback(self, body, **_):
        pprint(body)

        cap = cv2.VideoCapture(0)  # Change only if you have more than one webcams
        _, image_np = cap.read()

        pprint(image_np.shape)
        body['picture'] = {'data': encode(image_np), 'shape': image_np.shape}
        body['path_done'].append(self.__class__.__name__)
        self.queue_manager.publish('ObjectDetection', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    camera_manager = CameraManager()
    camera_manager.run()


if __name__ == '__main__':
    main()
