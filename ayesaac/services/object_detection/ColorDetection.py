import numpy as np
from PIL import Image
from skimage.color import rgb2lab
from skimage.segmentation import slic
from skimage.measure import regionprops
from pprint import pprint
import matplotlib.pyplot as plt
import pandas as pd


class ColorDetection:
    
    def __init__(self):
        color_list = pd.read_csv('../../data/color/lab.txt', skiprows=28, header=None, names=["l", "a", "b", "name"])
        color_list = color_list.values.tolist()[1:]
        self.color_list_names = [x[3] for x in color_list]
        self.color_list_values = [np.asarray(x[:3], dtype=np.float32) for x in color_list]        
    
    @staticmethod
    def open_image(file_path: str):
        image = Image.open(file_path)
        return np.array(image, dtype=np.float32)
    
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
        labelled_image = slic(lab_image, n_segments=200,
                              compactness=10,
                              sigma=0.1,
                              convert2lab=False,
                              enforce_connectivity=True)
        
        return labelled_image
    
    @staticmethod
    def create_regions(lab_image, labelled_image):
        region_segments = regionprops(labelled_image)
        
        image_dimensions = np.shape(labelled_image)
        
        for region in region_segments:
            region.is_boundary = ColorDetection.is_region_on_boundary(region, image_dimensions)
            region.average_color = ColorDetection.get_region_average_color(
                    region.label,
                    labelled_image,
                    lab_image
            )
        
        return region_segments
    
    @staticmethod
    def is_region_on_boundary(region, image_dimensions):
        if region.bbox[0] == 0 or region.bbox[1] == 0 or region.bbox[2] == \
                image_dimensions[0] or region.bbox == image_dimensions[1]:
            return True
        
        return False
    
    @staticmethod
    def get_pixels_from_label_id(label_id, labelled_image, image):
        label_mask = np.invert(np.isin(labelled_image, label_id))
        label_mask = np.dstack((label_mask, label_mask, label_mask))
        
        image_mask = np.ma.array(image, mask=label_mask)
        
        return image_mask
    
    @staticmethod
    def get_region_average_color(label_id, labelled_image, image):
        masked_image = ColorDetection.get_pixels_from_label_id(label_id, labelled_image,
                                                     image)
        
        flattened_masked_image = ColorDetection.flatten_image(masked_image)
        
        average_color = np.zeros(3, dtype=np.float32)
        
        for channel in range(np.shape(image)[2]):
            average_color[channel] = np.mean(flattened_masked_image[:, channel])
        
        return average_color
    
    @staticmethod
    def get_all_region_colors(region_list):
        return [region.average_color for region in region_list]

    def run(self, file_path):
        rgb_image = self.open_image(file_path)
        lab_image = self.convert_rgb_to_lab(rgb_image)
        labelled_image = self.create_labelled_image(lab_image)
        region_list = self.create_regions(lab_image, labelled_image)
        colors = self.get_all_region_colors(region_list)
        
        print("List of lab colors: ")
        pprint(self.color_list_values)
        print()
        print("Image colors: ")
        pprint(colors)
        print()
        
        colors_found = {}
        for color in colors:
            d = ((self.color_list_values - color) ** 2).sum(axis=1)
            if not self.color_list_names[d.argmax()] in colors_found:
                colors_found[self.color_list_names[d.argmax()]] = 0
            colors_found[self.color_list_names[d.argmax()]] += 1
        pprint(colors_found)
            
            
if __name__ == "__main__":
    
    # File which was used for testing
    # FILE_PATH = "data/katie-smith-uQs1802D0CQ-unsplash.jpg"
    
    # colors
    FILE_PATH = "test.jpg"
    color_detect = ColorDetection()
    color_detect.run(FILE_PATH)
    
