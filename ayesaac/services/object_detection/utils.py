

def calculate_iou(bbox1, bbox2, img_height, img_width):
    '''Method to calculate IoU of two bounding boxes'''
    
    # get the bounding box normalised coords
    ymin1, xmin1, ymax1, xmax1 = tuple(bbox1)
    ymin2, xmin2, ymax2, xmax2 = tuple(bbox2)
    
    # convert the normalised coords to absolute coords
    (top1, top2, bottom1, bottom2) = (img_height * ymin1, img_height * ymin2,
                                    img_height * ymax1, img_height * ymax2)
    (left1, left2, right1, right2) = (img_width * xmin1, img_width * xmin2,
                                    img_width * xmax1, img_width * xmax2)
    
    # get the intersecting coordinates
    xmin = max(left1, left2)
    xmax = min(right1, right2)
    ymin = max(top1, top2)
    ymax = min(bottom1, bottom2)
    
    # calculate the area of intersection
    intersection = (xmax - xmin) * (ymax - ymin)
    
    # calculate the area of both bboxes
    bbox1_area = (right1 - left1) * (bottom1 - top1)
    bbox2_area = (right2 - left2) * (bottom2 - top2)
    
    # calculate the area of the union
    union = bbox1_area + bbox2_area - intersection
    
    # calculate the intersection over the union
    iou = intersection / union
    
    return iou