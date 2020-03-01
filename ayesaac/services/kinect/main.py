
import cv2
from pprint import pprint

from services_lib.queues.queue_manager import QueueManager
from services_lib.images.crypter import encode

from pykinect2 import PyKinectV2
# from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cv2
import sys

DEPTH_MODE=PyKinectV2.FrameSourceTypes_Depth
COLOR_MODE=PyKinectV2.FrameSourceTypes_Color

class Kinect(object):
    """
    The class Kinect goal is to take a picture and send it back to CameraManager.
    """

    def __init__(self, mode=COLOR_MODE):
        self.kinect = PyKinectRuntime.PyKinectRuntime(mode)
        if mode & DEPTH_MODE:
            self.kinect_frame_size = (self.kinect.depth_frame_desc.Height, self.kinect.depth_frame_desc.Width)
        if mode & COLOR_MODE:
            self.kinect_frame_size = (self.kinect.color_frame_desc.Height, self.kinect.color_frame_desc.Width, -1)
        self.transform = mode & DEPTH_MODE and cv2.COLOR_GRAY2RGB or cv2.COLOR_RGBA2RGB
        self.queue_manager = QueueManager([self.__class__.__name__, 'CameraManager'])

    def get_colored_frame(self, size=None):
        frame = self.kinect.get_last_color_frame()
        frame = frame.reshape(self.kinect_frame_size).astype(np.uint8)
        frame = cv2.cvtColor(frame, self.transform)
        if size:
            return cv2.resize(frame, size)
        return frame

    def callback(self, body, **_):
        cap = cv2.VideoCapture(0)
        _, image_np = cap.read()

        # if mode & DEPTH_MODE:
        #     frame = _kinect.get_last_depth_frame()
        #     frameD = _kinect._depth_frame_data
        #     draw = True

        # if mode & COLOR_MODE and _kinect.has_new_color_frame():
        frame = self.get_colored_frame()

        pprint(frame.shape)
        body['picture'] = {'data': encode(frame), 'shape': frame.shape, 'from': self.__class__.__name__}
        self.queue_manager.publish('CameraManager', body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    web_cam = Kinect()
    web_cam.run()


if __name__ == '__main__':
    main()
