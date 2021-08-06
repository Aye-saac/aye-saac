from pprint import pprint

import keras_ocr
import numpy as np
from spellchecker import SpellChecker

import matplotlib

from ayesaac.services.common import QueueManager
from ayesaac.services.common.crypter import decode
from ayesaac.utils.logger import get_logger

from .bounding_box_to_phrases import bb_to_text
from .skew_correction import getSkewAngle
from .skew_correction import rotate_image

from ayesaac.services.common.group_6_config_interface import get_value

try:
	from PIL import Image
except ImportError:
	import Image
import pytesseract


logger = get_logger(__file__)

class OCR(object):
	"""
	The class OCR purpose is to detect all the possible text in the picture.
	"""

	if (get_value("default-ocr-model") == "keras-ocr"):
		def __init__(self):
			self.queue_manager = QueueManager([self.__class__.__name__, "LabelFormatter", "Interpreter"])
			self.pipeline = keras_ocr.pipeline.Pipeline()

		def callback(self, body, **_):
			logger.info("attempt-skew-correction: " + get_value("attempt-skew-correction"))

			image = [
				decode(body["pictures"][0]["data"], body["pictures"][0]["shape"], np.uint8)
			]

			if (get_value("attempt-skew-correction") == "false"):
				predictions = self.pipeline.recognize(image)[0]
				text = bb_to_text(predictions, False)
			elif (get_value("attempt-skew-correction") == "true"):
				attempt = 0
				text = None
				noSkewimages = []
				noSkewimages.append(None)

				# while (attempt < 4):
				while (attempt < 1):
					# ----- TODO: check syntax (either "image[0]" or simply "image") ------
					# Skew correction (USELESS?)
					noSkewimages[0] = rotate_image(image[0], -getSkewAngle(image[0]))
					# ---------------------------------------------------------------------

					predictions = self.pipeline.recognize(image)[0]

					# ------ APPROXIMATE CONFIDENCE RATING --------------------------------
					rawText = bb_to_text(predictions, False)

					spell = SpellChecker()
					nbTotalWords = 0;
					nbCorrectWords = 0;

					for j in range(0, len(rawText)):
						nbTotalWords = nbTotalWords + len(rawText[j]);
						nbCorrectWords = nbCorrectWords + len(spell.known(rawText[j]))

					percentage = nbCorrectWords/nbTotalWords * 100

					if( percentage < 50 ):
						logger.info("Cannot read this confidently, reorientating the object.")
						image = np.rot90(image) # This method prevent edges being cut during rotation
						attempt = attempt + 1
					else:
						logger.info("Read successfully.")
						text = bb_to_text(predictions, True);
						attempt = 4; # "while" exit condition
					# ---------------------------------------------------------------------

			body["texts"] = text
			body["path_done"].append(self.__class__.__name__)
			del body["pictures"]
			next_service = body["vision_path"].pop(0)
			self.queue_manager.publish(next_service, body)

			logger.info(f"{self.__class__.__name__} ready")

		def run(self):
			self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


	elif (default_ocr_model == "tesseract"):
		def __init__(self):
			self.queue_manager = QueueManager([self.__class__.__name__, "LabelFormatter", "Interpreter"])

		def callback(self, body, **_):

			pytesseract.pytesseract.tesseract_cmd = r'../usr/bin/tesseract'

			image = [
				decode(body["pictures"][0]["data"], body["pictures"][0]["shape"], np.uint8)
			]

			text = pytesseract.image_to_string(image[0])

			body["texts"] = text
			body["path_done"].append(self.__class__.__name__)
			del body["pictures"]
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
