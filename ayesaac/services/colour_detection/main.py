import operator
from pathlib import Path
from pprint import pprint

import numpy as np
import pandas as pd
from skimage.color import rgb2lab
from skimage.measure import regionprops
from skimage.segmentation import slic

from ayesaac.queue_manager import QueueManager
from ayesaac.queue_manager.crypter import decode
from ayesaac.utils.logger import get_logger


logger = get_logger(__file__)


class ColourDetection:
    """
    The class ColourDetection purpose is to detect every main colour from objects in
    the given pictures.
    """

    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

        project_root = Path(__file__).parent.parent.parent.parent
        data_file = f"{project_root}/ayesaac/data/colour/lab.txt"

        colour_list = pd.read_csv(
            data_file, skiprows=28, header=None, names=["l", "a", "b", "name"]
        )
        colour_list = colour_list.values.tolist()[1:]
        self.colour_list_names = [x[3] for x in colour_list]
        self.colour_list_values = np.asarray(
            [np.asarray(x[:3], dtype=np.float32) for x in colour_list]
        )

        logger.info(f"{self.__class__.__name__} ready")

    @staticmethod
    def convert_rgb_to_lab(image: np.ndarray) -> np.ndarray:
        return rgb2lab(image)

    @staticmethod
    def flatten_image(image: np.ndarray) -> np.ndarray:
        dimensions = np.shape(image)

        return np.reshape(image, (dimensions[0] * dimensions[1], dimensions[2]))

    @staticmethod
    def remove_non_unique_pixels(image: np.ndarray) -> np.ndarray:
        return np.unique(image, axis=0)

    @staticmethod
    def create_labelled_image(lab_image) -> np.ndarray:
        labelled_image = slic(
            lab_image,
            n_segments=200,
            compactness=10,
            sigma=0.1,
            convert2lab=False,
            enforce_connectivity=True,
        )

        return labelled_image

    @staticmethod
    def create_regions(lab_image, labelled_image):
        region_segments = regionprops(labelled_image)
        image_dimensions = np.shape(labelled_image)

        for region in region_segments:
            region.is_boundary = ColourDetection.is_region_on_boundary(
                region, image_dimensions
            )
            region.average_colour = ColourDetection.get_region_average_colour(
                region.label, labelled_image, lab_image
            )

        return region_segments

    @staticmethod
    def is_region_on_boundary(region, image_dimensions):
        if (
            region.bbox[0] == 0
            or region.bbox[1] == 0
            or region.bbox[2] == image_dimensions[0]
            or region.bbox == image_dimensions[1]
        ):
            return True
        return False

    @staticmethod
    def get_pixels_from_label_id(label_id, labelled_image, image):
        label_mask = np.invert(np.isin(labelled_image, label_id))
        label_mask = np.dstack((label_mask, label_mask, label_mask))
        image_mask = np.ma.array(image, mask=label_mask)
        return image_mask

    @staticmethod
    def get_region_average_colour(label_id, labelled_image, image):
        masked_image = ColourDetection.get_pixels_from_label_id(
            label_id, labelled_image, image
        )
        flattened_masked_image = ColourDetection.flatten_image(masked_image)
        average_colour = np.zeros(3, dtype=np.float32)

        for channel in range(np.shape(image)[2]):
            average_colour[channel] = np.mean(flattened_masked_image[:, channel])

        return average_colour

    @staticmethod
    def get_all_region_colours(region_list):
        return [region.average_colour for region in region_list]

    def detect_colours(self, crop_image):
        lab_image = self.convert_rgb_to_lab(crop_image)
        labelled_image = self.create_labelled_image(lab_image)
        region_list = self.create_regions(lab_image, labelled_image)
        colours = self.get_all_region_colours(region_list)

        colours_found = {}
        for colour in colours:
            d = ((self.colour_list_values - colour) ** 2).sum(axis=1)
            if not self.colour_list_names[d.argmin()] in colours_found:
                colours_found[self.colour_list_names[d.argmin()]] = 0
            colours_found[self.colour_list_names[d.argmin()]] += 1
        sorted_colours = max(colours_found.items(), key=operator.itemgetter(1))
        pprint(colours_found)
        return sorted_colours[0]

    def callback(self, body, **_):
        body["path_done"].append(self.__class__.__name__)

        for picture in body["pictures"]:
            image = decode(picture["data"], picture["shape"], np.uint8)
            for i, obj in enumerate(body["objects"]):
                crop_img = image[
                    int(picture["shape"][0] * obj["bbox"][0]) : int(
                        picture["shape"][0] * obj["bbox"][2]
                    ),
                    int(picture["shape"][1] * obj["bbox"][1]) : int(
                        picture["shape"][1] * obj["bbox"][3]
                    ),
                ]
                colour_name = self.detect_colours(crop_img)
                body["objects"][i]["colour"] = colour_name
        del body["pictures"]
        pprint(body)
        next_service = body["vision_path"].pop(0)
        self.queue_manager.publish(next_service, body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    colour_detection = ColourDetection()
    colour_detection.run()


if __name__ == "__main__":
    main()
