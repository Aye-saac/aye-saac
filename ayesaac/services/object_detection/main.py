from pprint import pprint

import numpy as np
import tensorflow as tf

from ayesaac.services.common import QueueManager
from ayesaac.services.common.crypter import decode
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger

from .coco_category_index import coco_category_index
from .epic_kitchens_category_index import epic_kitchens_category_index
from .plot_bounding_boxes import draw_bounding_boxes
from .utils import calculate_iou

logger = get_logger(__file__)
config = Config()


class ObjectDetection(object):
    """
    The class ObjectDetection purpose is to detect every object in the given pictures.
    """
    
    # define constants
    # confidence threshold for retaining object detection
    CONFIDENCE_THRESHOLD = 0.5
    # IoU threshold for determining whether detections are overlapping
    IOU_THRESHOLD = 0.5
    # list of model preferences for selecting detection
    MODEL_PREFS = ["coco", "epic-kitchens"]
    
    def __init__(self):
        self.queue_manager = QueueManager(
            [
                self.__class__.__name__,
                "Interpreter",
                "ColourDetection",
                "PositionDetection",
            ]
        )
        
        self.models = [
            {
                "name": "coco",
                "model_path": config.directory.data.joinpath("coco_resnet"),
                "category_index": coco_category_index
            },
            {
                "name": "epic-kitchens",
                "model_path": config.directory.data.joinpath("epic_kitchens"),
                "category_index": epic_kitchens_category_index
            }
        ]
        
        for model in self.models:
            tf_model = tf.saved_model.load(str(model["model_path"]))
            model["model"] = tf_model.signatures["serving_default"]
            
        logger.info(f"{self.__class__.__name__} ready")

    def run_inference_for_single_image(self, image, model):
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        output_dict = model(input_tensor)

        num_detections = int(output_dict.pop("num_detections"))
        output_dict = {
            key: value[0, :num_detections].numpy() for key, value in output_dict.items()
        }
        output_dict["num_detections"] = num_detections
        output_dict["detection_classes"] = output_dict["detection_classes"].astype(
            np.int32
        )
        return output_dict
    
    def filter_objects(self, objects, img_height, img_width):
        '''Method to filter duplicate detections from the output'''
        retained_objects = []
        for obj in objects:
            retain = True
            # duplicates are of the same class and have very high IoU
            for other_obj in objects:
                # ignore self
                if obj == other_obj:
                    continue
                else:
                    # calculate the IoU
                    iou = calculate_iou(obj["bbox"], other_obj["bbox"], img_height, img_width)
                    # check if IoU is greater than threshold
                    if iou >= ObjectDetection.IOU_THRESHOLD:
                        # we have a duplicate, don't retain the object if the model preference is lower
                        if ObjectDetection.MODEL_PREFS.index(obj["model"]) > ObjectDetection.MODEL_PREFS.index(other_obj["model"]):
                            retain = False
                            break
            
            # append the object if it's okay
            if retain:
                retained_objects.append(obj)
        
        return retained_objects
        
    def callback(self, body, **_):
        all_objects = []
        for picture in body["pictures"]:
            objects = []
            image = decode(picture["data"], picture["shape"], np.uint8)
            img_height = picture["shape"][0]
            img_width = picture["shape"][1]

            # iterate through the models, performing object detection
            for model in self.models:
                output = self.run_inference_for_single_image(image, model["model"])
                for i in range(output["num_detections"]):
                    if float(output["detection_scores"][i]) >= ObjectDetection.CONFIDENCE_THRESHOLD:
                        bbox = output["detection_boxes"][i].tolist()
                        objects.append(
                            {
                                "name": model["category_index"][output["detection_classes"][i]][
                                    "name"
                                ],
                                "confidence": float(output["detection_scores"][i]),
                                "bbox": bbox,
                                "from": picture["from"],
                                "model": model["name"],
                                "img_height": img_height,
                                "img_width": img_width
                            }
                        )
                        
            bboxes = [obj["bbox"] for obj in objects]
            class_names = [obj["name"] for obj in objects]
            scores = [obj["confidence"] for obj in objects]
            
            # draw the bounding boxes
            # (outputs image to docker/volumes/aye-saac_output_data/_data/bbox_[timestamp].png)
            draw_bounding_boxes(image, bboxes, class_names, scores, prefix="bbox")
            
            # need to filter the results to remove massively overlapping object detections
            # (this can arise when different models identify the same object for example)
            objects = self.filter_objects(objects, img_height, img_width)
            
            bboxes = [obj["bbox"] for obj in objects]
            class_names = [obj["name"] for obj in objects]
            scores = [obj["confidence"] for obj in objects]

            # draw the bounding boxes
            # (outputs image to docker/volumes/aye-saac_output_data/_data/bbox_[timestamp].png)
            draw_bounding_boxes(image, bboxes, class_names, scores, prefix="bbox_filtered")
            
            # append the objects to all_objects
            all_objects.extend(objects)
            
        # pprint(objects)
        body["objects"] = all_objects
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
