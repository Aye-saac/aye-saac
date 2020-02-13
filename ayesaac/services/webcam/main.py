
import cv2
from pprint import pprint

from ayesaac.services_lib.queues.queue_manager import QueueManager
from ayesaac.services_lib.images.crypter import encode


class WebCam(object):
    """
    The class WebCam goal is to take a picture and send it back to CameraManager.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, 'CameraManager'])

    def callback(self, body, **_):
        cap = cv2.VideoCapture(0)
        _, image_np = cap.read()

        pprint(image_np.shape)
        body['picture'] = {'data': encode(image_np), 'shape': image_np.shape, 'from': self.__class__.__name__}
        self.queue_manager.publish('CameraManager', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    web_cam = WebCam()
    web_cam.run()


if __name__ == '__main__':
    main()
