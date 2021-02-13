from pprint import pprint

import numpy as np
import tensorflow as tf

from ayesaac.services.common import QueueManager
from ayesaac.services.common.crypter import decode
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger

from .coco_category_index import coco_category_index
from .epic_kitchens_category_index import epic_kitchens_category_index


logger = get_logger(__file__)
config = Config()


class ObjectDetection(object):
    """
    The class ObjectDetection purpose is to detect every object in the given pictures.
    """

    def __init__(self):
        self.queue_manager = QueueManager(
            [
                self.__class__.__name__,
                "Interpreter",
                "ColourDetection",
                "PositionDetection",
            ]
        )
        self.category_index = epic_kitchens_category_index

        self.model_path = config.directory.data.joinpath("epic_kitchens")
        model = tf.saved_model.load(str(self.model_path))
        self.model = model.signatures["serving_default"]

        logger.info(f"{self.__class__.__name__} ready")

    def run_inference_for_single_image(self, image):
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        output_dict = self.model(input_tensor)

        num_detections = int(output_dict.pop("num_detections"))
        output_dict = {
            key: value[0, :num_detections].numpy() for key, value in output_dict.items()
        }
        output_dict["num_detections"] = num_detections
        output_dict["detection_classes"] = output_dict["detection_classes"].astype(
            np.int32
        )
        return output_dict

    def callback(self, body, **_):
        objects = []
        for picture in body["pictures"]:
            image = decode(picture["data"], picture["shape"], np.uint8)
            output = self.run_inference_for_single_image(image)
            for i in range(output["num_detections"]):
                if float(output["detection_scores"][i]) >= 0.5:
                    objects.append(
                        {
                            "name": self.category_index[output["detection_classes"][i]][
                                "name"
                            ],
                            "confidence": float(output["detection_scores"][i]),
                            "bbox": output["detection_boxes"][i].tolist(),
                            "from": picture["from"],
                        }
                    )
        pprint(objects)
        body["objects"] = objects
        body["path_done"].append(self.__class__.__name__)

        if "ColourDetection" not in body["vision_path"]:
            del body["pictures"]

        next_service = body["vision_path"].pop(0)
        self.queue_manager.publish(next_service, body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    obj_detection = ObjectDetection()
    obj_detection.run()


if __name__ == "__main__":
    main()
