import numpy as np
from PIL import Image
from skimage.color import rgb2lab
from skimage.segmentation import slic
from skimage.measure import regionprops


class ColorDetection:
    
    def __init__(self, file_path):
        self.rgb_image = self.open_image(file_path)
        self.lab_image = self.convert_rgb_to_lab(self.rgb_image)
        
        self.labelled_image = self.create_labelled_image()
        self.region_list = self.create_regions()
        
        self.color_list = self.get_all_region_colors(self.region_list)
    
    @staticmethod
    def open_image(file_path: str):
        image = Image.open(file_path)
        return np.array(image)
    
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
    
    def create_labelled_image(self) -> np.ndarray:
        labelled_image = slic(self.lab_image, n_segments=200,
                              compactness=10,
                              sigma=0.1,
                              convert2lab=False,
                              enforce_connectivity=True)
        
        return labelled_image
    
    def create_regions(self):
        region_segments = regionprops(self.labelled_image)
        
        image_dimensions = np.shape(self.labelled_image)
        
        for region in region_segments:
            region.is_boundary = self.is_region_on_boundary(region,
                                                            image_dimensions)
            region.average_color = self.get_region_average_color(
                    region.label,
                    self.labelled_image,
                    self.lab_image
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
    
    def get_region_average_color(self, label_id, labelled_image, image):
        masked_image = self.get_pixels_from_label_id(label_id, labelled_image,
                                                     image)
        
        flattened_masked_image = self.flatten_image(masked_image)
        
        average_color = np.zeros(3)
        
        for channel in range(np.shape(image)[2]):
            average_color[channel] = np.mean(flattened_masked_image[:, channel])
        
        return average_color
    
    @staticmethod
    def get_all_region_colors(region_list):
        return [region.average_color for region in region_list]


if __name__ == "__main__":
    
    # File which was used for testing
    # FILE_PATH = "data/katie-smith-uQs1802D0CQ-unsplash.jpg"
    
    # colors
    color_detect = ColorDetection(FILE_PATH)
