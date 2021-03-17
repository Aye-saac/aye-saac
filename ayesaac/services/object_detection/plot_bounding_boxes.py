import matplotlib.pyplot as plt
import numpy as np
import time

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

from ayesaac.utils.config import Config

config = Config()


def draw_bounding_boxes(image, bboxes, class_names, scores, prefix="bbox"):
    """Draw bounding boxes and labels on supplied image"""
    fig = plt.figure(figsize=(40, 15))
    img = draw_boxes(image, bboxes, class_names, scores)
    plt.imshow(img)
    fig.savefig(f"{config.directory.output}/{prefix}_{time.time()}.png", dpi = 180)


def draw_boxes(image, bboxes, class_names, scores, max_boxes=10):
    """Overlay labeled boxes on an image with formatted scores and label names.
    Adapted from https://www.tensorflow.org/hub/tutorials/object_detection"""

    # Make sure the max boxes is not greater than the number of boxes
    if (len(bboxes) < max_boxes): max_boxes = len(bboxes)
    
    # Generate a list of colours for the bounding boxes
    colours = list(ImageColor.colormap.values())

    # Iterate through the bounding boxes, drawing them on the image one by one
    for i in range(0, max_boxes):
        bbox = bboxes[i]
        display_str = "{}: {}%".format(class_names[i], int(100 * scores[i]))
        colour = colours[-i]
        image_pil = Image.fromarray(np.uint8(image)).convert("RGB")
        draw_bounding_box_on_image(image_pil, bbox, colour, display_str=display_str)
        
        # Overwrite image to retain the bounding box
        image = image_pil
        
    return image


def draw_bounding_box_on_image(image, bbox, colour, thickness=3, display_str=""):
    """Adds a bounding box to an image.
    Adapted from https://www.tensorflow.org/hub/tutorials/object_detection"""
    
    # Get the box coordinates
    ymin, xmin, ymax, xmax = tuple(bbox)
    
    # Draw the image
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                ymin * im_height, ymax * im_height)
    
    # Draw the bounding box
    draw.line([(left, top), (left, bottom), (right, bottom), (right, top),
                (left, top)],
            width=thickness,
            fill=colour)

    # Set font
    font = ImageFont.load_default()
    
    # Prepare the bounding box label, start by getting label height from font
    display_str_height = font.getsize(display_str)[1]
    
    # Determine whether the text should be rendered above or below the line
    # based on a threshold of 1.1 * height
    total_display_str_height = 1.1 * display_str_height

    if top > total_display_str_height:
        text_bottom = top
    else:
        text_bottom = top + total_display_str_height
    
    # Render the bbox label
    text_width, text_height = font.getsize(display_str)
    margin = np.ceil(0.05 * text_height)
    draw.rectangle([(left, text_bottom - text_height - 2 * margin),
                    (left + text_width, text_bottom)],
                    fill=colour)
    draw.text((left + margin, text_bottom - text_height - margin),
                display_str,
                fill="black",
                font=font)
    text_bottom -= text_height - 2 * margin
