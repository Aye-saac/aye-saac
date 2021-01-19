import copy

from ayesaac.queue_manager import QueueManager
from ayesaac.utils.logger import get_logger


logger = get_logger(__file__)


class CameraManager(object):
    """
    The class CameraManager goal is to organise the collect of pictures from different
     camera sources.
    """

    def __init__(self):
        self.queue_manager = QueueManager(
            [self.__class__.__name__, "WebCam", "WebCamBis", "ObjectDetection", "OCR"]
        )
        self.camera_names = ["WebCam"]
        self.pictures = []
        self.waiting_cameras = 0
        self.save_body = None

        logger.info(f"{self.__class__.__name__} ready")

    def from_cameras(self, body):
        logger.info("Receiving picture from: ", body["picture"]["from"])
        logger.info(body)
        self.pictures.append(body["picture"])
        self.waiting_cameras -= 1

    def request_pictures_from_all_concern_cameras(self):
        logger.info("Request pictures !")
        self.waiting_cameras = len(self.camera_names)
        for camera_name in self.camera_names:
            self.queue_manager.publish(camera_name, {"nb_picture": 1})

    def callback(self, body, **_):
        logger.info("Callback triggered")
        if "run_as_webservice" in body:
            # skip running cameras, we have an image!
            logger.info(
                "Camera management: don't use cameras as running in webservice mode."
            )
            assert "pictures" in body
            next_service = body["vision_path"].pop(0)
            body["path_done"].append(self.__class__.__name__)
            self.queue_manager.publish(next_service, body)

        elif self.waiting_cameras:
            self.from_cameras(body)
            if not self.waiting_cameras:
                self.save_body["pictures"] = copy.deepcopy(self.pictures)
                self.save_body["path_done"].append(self.__class__.__name__)
                logger.info("Send pictures !")

                # for path in self.save_body['vision_path']:
                # body_ = self.save_body
                # body_['vision_path'] = path
                next_service = self.save_body["vision_path"].pop(0)
                self.queue_manager.publish(next_service, self.save_body)
                self.pictures = []
                self.save_body = None
        else:
            self.request_pictures_from_all_concern_cameras()
            self.save_body = body

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    camera_manager = CameraManager()
    camera_manager.run()


if __name__ == "__main__":

    main()
