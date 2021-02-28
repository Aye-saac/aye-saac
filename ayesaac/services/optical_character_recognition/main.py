from pprint import pprint

import keras_ocr
import numpy as np

import matplotlib

from ayesaac.services.common import QueueManager
from ayesaac.services.common.crypter import decode
from ayesaac.utils.logger import get_logger

from .bounding_box_to_phrases import bb_to_text


logger = get_logger(__file__)


'''
OCR_OLD (previously OCR) was ayesaac's optical character recognition service. It
seems to have trouble finding the keras-ocr model and doesn't work because of this.

See the OCR class below for a possible replacement using pytesseract.
'''
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

        # Recomment this
        # fig, axs = plt.subplots(nrows=len(image), figsize=(20, 20))
        # keras_ocr.tools.drawAnnotations(image=image[0], predictions=predictions, ax=axs)
        # plt.show()


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



try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

class OCR_TEST(object):
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

    def callback(self, body, **_):

        pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

        image = [
            decode(body["pictures"][0]["data"], body["pictures"][0]["shape"], np.uint8)
        ]

        text = pytesseract.image_to_string(image[0])

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
