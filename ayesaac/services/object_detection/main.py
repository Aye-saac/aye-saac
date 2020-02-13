
import pprint
import numpy as np
import tensorflow as tf
from pathlib import Path

from ayesaac.services_lib.queues.queue_manager import QueueManager
from ayesaac.services_lib.images.crypter import decode
from ayesaac.data.models.coco_category_index import coco_category_index


class ObjectDetection(object):
    """
    The class ObjectDetection purpose is to detect every object in the given pictures.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])
        self.category_index = coco_category_index
        self.model_path = Path("./data/models/ssd_resnet50_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03/saved_model")
        model = tf.saved_model.load(str(self.model_path))
        self.model = model.signatures['serving_default']

    def run_inference_for_single_image(self, image):
        image = np.asarray(image)
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        output_dict = self.model(input_tensor)

        num_detections = int(output_dict.pop('num_detections'))
        output_dict = {key: value[0, :num_detections].numpy()
                       for key, value in output_dict.items()}
        output_dict['num_detections'] = num_detections
        output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int32)
        return output_dict

    def callback(self, body, **_):
        objects = []
        for picture in body['pictures']:
            image = decode(picture['data'], picture['shape'], np.uint8)
            output = self.run_inference_for_single_image(image)
            for i in range(output['num_detections']):
                objects.append({
                    'name': self.category_index[output['detection_classes'][i]]['name'],
                    'confidence': float(output['detection_scores'][i]),
                    'bbox': output['detection_boxes'][i].tolist(),
                    'from': picture['from']
                })
        pprint.pprint(objects)
        body['objects'] = objects
        body['path_done'].append(self.__class__.__name__)
        del body['pictures']
        self.queue_manager.publish("Interpreter", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    obj_detection = ObjectDetection()
    obj_detection.run()


if __name__ == "__main__":
    main()
