from pprint import pprint

import keras_ocr
import numpy as np

from ayesaac.queue_manager import QueueManager
from ayesaac.queue_manager.crypter import decode
from ayesaac.utils.logger import get_logger

from .bounding_box_to_phrases import bb_to_text


logger = get_logger(__file__)


class OCR(object):
    """
    The class OCR purpose is to detect all the possible text in the picture.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])
        self.pipeline = keras_ocr.pipeline.Pipeline()

    def callback(self, body, **_):
        image = [
            decode(body["pictures"][0]["data"], body["pictures"][0]["shape"], np.uint8)
        ]
        predictions = self.pipeline.recognize(image)[0]

        """fig, axs = plt.subplots(nrows=len(image), figsize=(20, 20))
        keras_ocr.tools.drawAnnotations(image=image[0], predictions=predictions, ax=axs)
        plt.show()"""
        pprint(predictions)
        text = bb_to_text(predictions)

        body["texts"] = text
        body["path_done"].append(self.__class__.__name__)
        del body["pictures"]
        pprint(body)
        next_service = body["vision_path"].pop(0)
        self.queue_manager.publish(next_service, body)

        logger.info(f"{self.__class__.__name__} ready")

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    ocr = OCR()
    ocr.run()


if __name__ == "__main__":
    main()
