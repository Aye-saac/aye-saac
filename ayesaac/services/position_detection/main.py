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
    
    Methods within use bounding boxes to determine positions relative to hands/anchors.
    
    A little reminder about bounding boxes returned from TensorFlow...
    The bounding box coordinates are (top, left, bottom and right) and are normalised
    to the image width/height (between 0 and 1).
    
    Example coordinates:
    * top    = 0.2
    * bottom = 0.4
    * left   = 0.3
    * right  = 0.6
    
    The bounding box will Look like this:
    
                   left (0.3)  right (0.6)
                      |          |
    top (0.2)    -----|----------|----
                      |          |
                      |          |
                      |          |
    bottom (0.4) -----|----------|----
                      |          |
                    
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
    
    def get_hand_position(self, obj, objects):
        '''Method identifies position relative to hands or people using bounding boxes'''
        
        # Set default to ""
        position_str = ""
        
        # Set the hand classes
        hand_classes = ["hand", "person"]
        
        # If the object is a hand itself, it does not need to be positioned 
        if obj["name"] in hand_classes:
            return position_str
            
        # Determine if there are hands in the image: use "hand" or "person" class name
        hand_objects = copy.deepcopy([o for o in objects if o["from"] == obj["from"] and o["name"] in hand_classes])
        if len(hand_objects) == 0:
            return position_str
        
        # Not going to be able to use hands to position if there are more than two in this image
        if len(hand_objects) > 2:
            return position_str
        
        # Now we have hands in the image, find the positioning
        # Get the bounding box normalised coords
        top_obj, left_obj, bottom_obj, right_obj = tuple(obj["bbox"])
        
        # get the central coords
        x_obj = (left_obj + right_obj) / 2
        y_obj = (top_obj + bottom_obj) / 2

        # If there are two objects, see if the object is positioned between the hands
        if len(hand_objects) == 2 and hand_objects[0]["name"] == "hand" and hand_objects[1]["name"] == "hand":
            
            if self.__obj_is_between_hands__(x_obj, y_obj, hand_objects):
                position_str = " is between hands"
                
        elif len(hand_objects) == 1:
            
            # Get the bounding box normalised coords
            top_hand, left_hand, bottom_hand, right_hand = tuple(hand_objects[0]["bbox"])
            
            # Get the midpoints
            x_hand = (left_hand + right_hand) / 2
            y_hand = (top_hand + bottom_hand) / 2
        
            if self.__obj_is_right_of_hand__(x_obj, x_hand):
                position_str = " is to the right of a " + hand_objects[0]["name"]
            
            if self.__obj_is_left_of_hand__(x_obj, x_hand):
                position_str = " is to the left of a " + hand_objects[0]["name"]
                
        return position_str
        
    
    def __obj_is_between_hands__(self, x_obj, y_obj, hand_objects):
        '''Method to determine if the object is between the hands'''
        is_between = False
        
        # Get the bounding boxes of the hands
        top_hand1, left_hand1, bottom_hand1, right_hand1 = tuple(hand_objects[0]["bbox"])
        top_hand2, left_hand2, bottom_hand2, right_hand2 = tuple(hand_objects[1]["bbox"])
        
        # get the central coords
        x_hand1 = (left_hand1 + right_hand1) / 2
        x_hand2 = (left_hand2 + right_hand2) / 2
        y_hand1 = (top_hand1 + bottom_hand1) / 2
        y_hand2 = (top_hand2 + bottom_hand2) / 2
        
        # determine if object is between hands
        if (x_hand1 < x_obj < x_hand2) or (x_hand1 > x_obj > x_hand2):
            is_between = True
        
        elif (y_hand1 < y_obj < y_hand2) or (y_hand1 > y_obj > y_hand2):
            is_between = True
        
        return is_between
    
    def __obj_is_right_of_hand__(self, x_obj, x_hand):
        '''Method to determine if the object is to the right of the hand'''
        if (x_obj > x_hand):
            return True
        else:
            return False
        
    def __obj_is_left_of_hand__(self, x_obj, x_hand):
        '''Method to determine if the object is to the left of the hand'''
        if (x_hand > x_obj):
            return True
        else:
            return False
        
    def get_anchored_position(self, obj, objects):
        '''Method identifies position relative to anchors, e.g. "next to fridge"'''

        # Set default to [] because anchored position may not be possible
        position_str_list = []
        
        # List the anchors in the image
        anchors = copy.deepcopy([o for o in objects if o["from"] == obj["from"] and o["name"] in ANCHORS.keys()])
        
        # Remove self from anchors
        if obj["name"] in [anchor["name"] for anchor in anchors]:
            anchors.remove(obj)
        
        # Determine if there are anchors in the image, if not return None
        if len(anchors) == 0:
            return position_str_list
        
        # Append the relationship info to anchors
        for anchor in anchors:
            anchor["relationships"] = ANCHORS[anchor["name"]]["relationships"]
        
        # Now we have anchors in the image, find the positioning relationship between the object and the anchor
        for anchor in anchors:
            
            # Get the bounding box normalised coords
            top_obj, left_obj, bottom_obj, right_obj = tuple(obj["bbox"])
            top_anchor, left_anchor, bottom_anchor, right_anchor = tuple(anchor["bbox"])
            
            if "in" in anchor["relationships"]:
                if self.__obj_is_on_anchor__(left_obj, left_anchor, right_obj, right_anchor,
                                         bottom_obj, bottom_anchor):
                    position_str_list.append(" it's in the " + anchor["name"])
                    continue
            
            if "on" in anchor["relationships"]:
                if self.__obj_is_on_anchor__(left_obj, left_anchor, right_obj, right_anchor,
                                         bottom_obj, bottom_anchor):
                    position_str_list.append(" it's on the " + anchor["name"])
                    continue
            
            if "next to" in anchor["relationships"]:
                if self.__obj_is_left_of_anchor__(left_obj, left_anchor, right_obj, right_anchor):
                    position_str_list.append(" it's left of the " + anchor["name"])
                    continue
                
                elif self.__obj_is_right_of_anchor__(left_obj, left_anchor, right_obj, right_anchor):
                    position_str_list.append(" it's right of the " + anchor["name"])
                    continue
                
            if "below" in anchor["relationships"]:
                if self.__obj_is_below_anchor__(left_obj, left_anchor, right_obj, right_anchor,
                                         top_obj, top_anchor):
                    position_str_list.append(" it's below the " + anchor["name"])
                    continue
            
            # Default position if the above conditions cannot be met
            position_str_list.append(" it's near the " + anchor["name"])
        
        return position_str_list
    
    def __obj_is_on_anchor__(self, left_obj, left_anchor, right_obj, right_anchor, bottom_obj, bottom_anchor):
        '''Method to determine whether obj is on/in anchor.'''
        is_on = False
        
        if (
            left_obj > left_anchor
            and right_obj < right_anchor
            and bottom_obj < bottom_anchor
            ):
            is_on = True
        
        return is_on

    def __obj_is_left_of_anchor__(self, left_obj, left_anchor, right_obj, right_anchor):
        '''Method to determine whether obj is left of anchor.'''
        is_left_of = False
        
        if (left_obj < left_anchor):
            is_left_of = True
        
        return is_left_of
    
    def __obj_is_right_of_anchor__(self, left_obj, left_anchor, right_obj, right_anchor):
        '''Method to determine whether obj is right of anchor.'''
        is_right_of = False
        
        if (right_obj > right_anchor):
            is_right_of = True
        
        return is_right_of
            
    def __obj_is_below_anchor__(self, left_obj, left_anchor, right_obj, right_anchor, top_obj, top_anchor):
        '''Method to determine whether obj is below anchor.'''
        is_below = False
        
        if (
            left_obj > left_anchor
            and right_obj < right_anchor
            and top_obj > top_anchor
            ):
            is_below = True
        
        return is_below

    def callback(self, body, **_):
        pprint(body)

        for i, obj in enumerate(body["objects"]):
            body["objects"][i]["lateral_position"] = self.get_lateral_position(obj)
            body["objects"][i]["anchored_position"] = self.get_anchored_position(obj, body["objects"])
            body["objects"][i]["hand_position"] = self.get_hand_position(obj, body["objects"])
            print("lateral_position: " + str(body["objects"][i]["lateral_position"]))
            print("anchored_position: " + str(body["objects"][i]["anchored_position"]))
            print("hand_position: " + str(body["objects"][i]["hand_position"]))

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
