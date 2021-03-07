import os
import copy
from pprint import pprint

from ayesaac.services.common import QueueManager
from ayesaac.utils.logger import get_logger

from .anchor_index import ANCHORS

logger = get_logger(__file__)


class PositionDetection(object):
    """
    The class PositionDetection purpose provide the global position of the detected objects.
    """
    
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

        logger.info(f"{self.__class__.__name__} ready")

    def get_lateral_position(self, obj, max_pos=(1, 1)):
        step = (max_pos[0] / 3, max_pos[1] / 3)
        center = (
            (obj["bbox"][0] + obj["bbox"][2]) / 2,
            (obj["bbox"][1] + obj["bbox"][3]) / 2,
        )
        if center[1] > 2 * step[1]:
            return " on the left"
        elif center[1] > step[1]:
            return " in the center"
        return " on the right"
    
    def get_anchored_position(self, obj, objects):
        '''Method identifies position relative to anchors, e.g. "next to fridge"'''

        # Set default to [] because anchored position may not be possible
        position_str_list = []
        
        # If the object is an anchor itself, it does not need to be anchored 
        if obj["name"] in ANCHORS.keys():
            return position_str_list
        
        # Determine if there are anchors in the image, if not return None
        anchors = copy.deepcopy([o for o in objects if o["from"] == obj["from"] and o["name"] in ANCHORS.keys()])
        if len(anchors) == 0:
            return position_str_list
        
        # append the relationship info to anchors
        for anchor in anchors:
            anchor["relationships"] = ANCHORS[anchor["name"]]["relationships"]
        
        # Now we have anchors in the image, find the relationship between the object and the anchor
        for anchor in anchors:
            
            # get the bounding box normalised coords
            top_obj, left_obj, bottom_obj, right_obj = tuple(obj["bbox"])
            top_anchor, left_anchor, bottom_anchor, right_anchor = tuple(anchor["bbox"])
            
            if "in" in anchor["relationships"]:
                if self.obj_is_on_anchor(left_obj, left_anchor, right_obj, right_anchor,
                                         bottom_obj, bottom_anchor):
                    position_str_list.append("in the " + anchor["name"])
                    continue
            
            if "on" in anchor["relationships"]:
                if self.obj_is_on_anchor(left_obj, left_anchor, right_obj, right_anchor,
                                         bottom_obj, bottom_anchor):
                    position_str_list.append("on the " + anchor["name"])
                    continue
            
            if "next to" in anchor["relationships"]:
                if self.obj_is_next_to_anchor(left_obj, left_anchor, right_obj, right_anchor):
                    position_str_list.append("next to the " + anchor["name"])
                    continue
                
            if "below" in anchor["relationships"]:
                if self.obj_is_below_anchor(left_obj, left_anchor, right_obj, right_anchor,
                                         bottom_obj, bottom_anchor):
                    position_str_list.append("below the " + anchor["name"])
                    continue
            
            # default position if the above conditions cannot be met
            position_str_list.append("near the " + anchor["name"])
        
        return position_str_list
    
    def obj_is_on_anchor(self, left_obj, left_anchor, right_obj, right_anchor, bottom_obj, bottom_anchor):
        '''Method to determine whether obj is on/in anchor.'''
        is_on = False
        
        if (
            left_obj > left_anchor
            and right_obj < right_anchor
            and bottom_obj < bottom_anchor
            ):
            is_on = True
        
        return is_on

    def obj_is_next_to_anchor(self, left_obj, left_anchor, right_obj, right_anchor):
        '''Method to determine whether obj is next to anchor.'''
        is_next_to = False
        
        if (
            left_obj < left_anchor
            or right_obj > right_anchor
            ):
            is_next_to = True
        
        return is_next_to
            
    def obj_is_below_anchor(self, left_obj, left_anchor, right_obj, right_anchor, bottom_obj, bottom_anchor):
        '''Method to determine whether obj is below anchor.'''
        is_below = False
        
        if (
            left_obj > left_anchor
            and right_obj < right_anchor
            and bottom_obj > bottom_anchor
            ):
            is_below = True
        
        return is_below

    def callback(self, body, **_):
        pprint(body)

        for i, obj in enumerate(body["objects"]):
            body["objects"][i]["lateral_position"] = self.get_lateral_position(obj)
            body["objects"][i]["anchored_position"] = self.get_anchored_position(obj, body["objects"])

        body["path_done"].append(self.__class__.__name__)
        next_service = body["vision_path"].pop(0)
        self.queue_manager.publish(next_service, body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    position_detection = PositionDetection()
    position_detection.run()


if __name__ == "__main__":
    main()
