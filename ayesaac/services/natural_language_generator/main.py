import os
from pprint import pprint
from random import choice

from ayesaac.services.common import QueueManager
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger

from ayesaac.services.common.group_6_config_interface import get_config
from ayesaac.services.common.group_6_config_interface import get_value
from ayesaac.services.common.group_6_config_interface import set_value
from ayesaac.services.common.group_6_config_interface import set_arr_value


config = Config()


logger = get_logger(__file__)

dairy = ["dairy", "milk", "butter", "cream", "cheese", "yogurt"]
nuts = ["nuts", "peanuts", "pecans", "walnuts", "almonds", "brazil nuts", "cashews",
    "chesnuts", "filberts", "hazelnuts", "macadamia", "pine nuts", "pistachios"]
meat = ["meat", "chicken", "pork", "beef", "veal"]
allergens = ["celery", "gluten", "crustaceans", "eggs", "fish", "lupin", "milk",
    "molluscs", "mustard", "peanuts", "sesame", "soybeans", "sulphur dioxide",
    "sulphites", "tree nuts"]


class NaturalLanguageGenerator(object):
    """
    The class NaturalLanguageGenerator purpose is to translate the results obtained to a nicely formatted sentence.
    """

    def __init__(self):
        self.queue_manager = QueueManager(
            [self.__class__.__name__, "ExternalInterface"]
        )
        self.answers = {}
        self.description_types = [
            "DESCRIPTION_NOTHING",
            "DESCRIPTION_ANSWER_S",
            "DESCRIPTION_ANSWER_P",
        ]
        self.build_generator()

        logger.info(f"{self.__class__.__name__} ready")

    def build_generator(self):
        folder_path = config.directory.data.joinpath("sentence_templates")
        for _, _, files in os.walk(folder_path):
            for name in files:
                with open(str(folder_path / name)) as f:
                    self.answers[name] = [line.strip() for line in f]

    def get_det(self, word):
        return str(word[1]) + " " if word[1] > 1 else "a "

    def generate_text(self, words, context, obj_cnt):
        answer = choice(self.answers[context])
        if type(words) == str:
            return answer.replace("*", words, 1)
        elif len(words) > 1:
            tmp = (
                ", ".join([self.get_det(w) + w[0] for w in words[:-1]])
                + " and "
                + self.get_det(words[-1])
                + words[-1][0]
            )
            return answer.replace("*", tmp, 1)
        elif len(words):
            return answer.replace(
                "*",
                ((str(words[0][1]) + " ") if words[0][1] > 1 else "") + words[0][0],
                1,
            )
        return answer

    def identify(self, body):
        pprint("identify")

        objects = []
        for o in body["objects"]:
            if o["name"] != "person":
                objects.append(
                    o["name"]
                    + (o["lateral_position"] if o.get("lateral_position") else "")
                )
        objects = list(set([(o, objects.count(o)) for o in objects]))
        obj_cnt = sum(n for _, n in objects)
        context = self.description_types[obj_cnt if obj_cnt < 2 else 2]
        return objects, context, obj_cnt

    def recognise(self, body):
        pprint("recognise")

        objects = []
        for o in body["objects"]:
            for p in body["intents"]["entities"]:
                if o["name"] == p["value"]:
                    objects.append(
                        o["name"]
                        + (o["lateral_position"] if o.get("lateral_position") else "")
                    )
        objects = list(set([(o, objects.count(o)) for o in objects]))
        obj_cnt = sum(n for _, n in objects)
        context = (
            ("POSITIVE" if obj_cnt > 0 else "NEGATIVE")
            + "_ANSWER_"
            + ("P" if obj_cnt > 1 else "S")
        )
        if not obj_cnt:
            objects = [(p["value"], 1) for p in body["intents"]["entities"]]
            obj_cnt = sum(n for _, n in objects)
        return objects, context, obj_cnt

    def read_text(self, body):
        pprint("read_text")

        objects = " ".join(" ".join(t) for t in body["texts"])
        obj_cnt = 1 if len(objects) > 0 else 0
        context = "READ_TEXT_" + ("POSITIVE" if obj_cnt > 0 else "NEGATIVE")
        return objects, context, obj_cnt

    def detect_safety(self, body):
        objects = ""
        obj_cnt = 1
        context = "SAFETY_CLARIFY"
        return objects, context, obj_cnt

    def inform_allergen(self, body):
        pprint("inform_allergen")
        allergen = body["intents"]["entities"][0]["value"]

        if allergen not in get_value("allergens"): #  if allegen not in list, add
            set_arr_value("allergens", allergen)
            print("Set allergen to list")
        else:
            print("Already in list")
        #set_value("allergen", allergen)
        print(get_value("allergens"))

        objects = allergen
        if (len(allergen) > 0):
            context = "ALLERGEN_ADDED_POSITIVE"
        else:
            context = "ALLERGEN_ADDED_NEGATIVE"
        print("Allergen detected: " + allergen + ". Added to list.")
        obj_cnt = 1 if len(allergen) > 0 else 0
        return objects, context, obj_cnt

    def detect_ingredients(self, body):
        pprint("detect_ingredients")
        label_json = body["extracted_label"]
        print(body["intents"])
        objects = ""

        ingredient = body["intents"]["entities"][0]["value"]
        print("Looking for " + ingredient + "...")
        if ingredient == "dairy":
            print("Looking for dairy products in ingredients...")
            for i in dairy:
                instances = label_json["ingredients"].split().count(i)
        elif ingredient == "nuts":
            print("Looking for nuts in ingredients...")
            for i in nuts:
                instances = label_json["ingredients"].split().count(i)
        elif ingredient == "meat":
            print("Looking for meat in ingredients...")
            for i in meat:
                instances = label_json["ingredients"].split().count(i)
        elif ingredient == "allergens":
            print("Looking for allergens in ingredients...")
            for i in allergens:
                instances = label_json["ingredients"].split().count(i)
        else:
            #ingredient_found = [ingredient == x for x in label_json["ingredients"].split()]
            instances = label_json["ingredients"].split().count(ingredient)

        print(instances)

        objects = ingredient
        all_ingredients = label_json["ingredients"].split()
        logger.info(label_json)
        if (len(all_ingredients) > 0):
            if (instances > 0):
                objects = ingredient
                context = "ALLERGENS_POSITIVE_ANSWER"
            else:
                objects = "This doesn't contain " + ingredient
                context = "ALLERGENS_NEGATIVE_ANSWER"
            print("Found " + str(instances) + " instances of " + ingredient + ".")
        else:
            context = "READ_TEXT_NEGATIVE"

        obj_cnt = 1 if len(all_ingredients) > 0 else 0
        #context = "READ_TEXT_" + ("POSITIVE" if obj_cnt > 0 else "NEGATIVE")
        return objects, context, obj_cnt

    #Assuming label formatter can detect Cooking instructions and classify it as "cooking_info"
    def cooking_info(self, body):
        pprint("cooking_info")
        label_json = body["extracted_label"]
        print(body["intents"])
        instructions = label_json["cooking_info"]
        objects = instructions
        logger.info(label_json)
        if (len(instructions) > 0):
            objects = instructions
            context = "READ_TEXT_POSITIVE"
        else:
            objects = ""
            context = "COOKING_INFO_NEGATIVE"

        obj_cnt = 1 if len(instructions) > 0 else 0
        return objects, context, obj_cnt

    #Assuming the label formatter can detect expiry date and classify it as "expiry_date"
    def detect_expiration(self, body):
        pprint("detect_expiration")
        label_json = body["extracted_label"]
        print(body["intents"])
        expiry_date = label_json["expiry_date"]
        objects = expiry_date

        if (len(expiry_date) > 0):
            context = "EXPIRY_DATE_POSITIVE_ANSWER"
        else:
            context = "EXPIRY_DATE_NEGATIVE_ANSWER"

        obj_cnt = 1 if len(expiry_date) > 0 else 0

        return objects, context, obj_cnt

    def detect_nutri(self, body):
        pprint("detect_nutri")
        label_json = body["extracted_label"]
        objects = ""
        print(label_json)
        key = "nutrition facts"
        objects += key + ": " + label_json[key]

        obj_cnt = 1 if len(objects) > 0 else 0
        context = "READ_TEXT_" + ("POSITIVE" if obj_cnt > 0 else "NEGATIVE")
        return objects, context, obj_cnt

    def detect_colour(self, body):
        pprint("detect_colour")

        obj_cnt = 0
        objects = None
        context = None

        for o in body["objects"]:
            for p in body["intents"]["entities"]:
                if o["name"] == p["value"]:
                    objects = (p["value"], o["colour"])
                    break
                else:
                    objects = (p["value"], None)
        if objects:
            obj_cnt = 1 if objects[1] else 0
            objects = objects[obj_cnt]
            context = "COLOR_DETECTION" if obj_cnt else "COLOR_DETECTION_N"
        return objects, context, obj_cnt

    def locate(self, body):
        pprint("locate")

        objects = []
        for o in body["objects"]:
            for p in body["intents"]["entities"]:
                if o["name"] == p["value"]:
                    if (
                        not o.get("lateral_position")
                        and o.get("bbox")
                        and len(o["bbox"]) >= 4
                    ):
                        bbox = o["bbox"]
                        yStart = bbox[0]
                        xStart = bbox[1]
                        yEnd = bbox[2]
                        xEnd = bbox[3]
                        xCenter = (xEnd + xStart) / 2
                        yCenter = (yEnd + yStart) / 2
                        pprint("xCenter")
                        pprint(xCenter)
                        if xCenter < 0.382:
                            o["lateral_position"] = " on the left"
                        elif xCenter >= 0.382 and xCenter <= 0.618:
                            o["lateral_position"] = " in front"
                        elif xCenter > 0.618:
                            o["lateral_position"] = " on the right"
                    objects.append(
                        o["name"]
                        + (o["lateral_position"] if o.get("lateral_position") else "")
                    )
        objects = list(set([(o, objects.count(o)) for o in objects]))
        obj_cnt = sum(n for _, n in objects)
        context = self.description_types[obj_cnt if obj_cnt < 2 else 2]
        return objects, context, obj_cnt

    def safety_info(self, body):
        objects = "test"
        obj_cnt = sum(n for _, n in objects)
        context = self.description_types[obj_cnt if obj_cnt < 2 else 2]
        return objects, context, obj_cnt

    def default(self, body):
        pprint("default")

        # Creates list of object detected in the scene
        objects = [
            o["name"] + (o["lateral_position"] if o.get("lateral_position") else "")
            for o in body["objects"]
        ]
        objects = list(set([(o, objects.count(o)) for o in objects]))
        obj_cnt = sum(n for _, n in objects)
        context = self.description_types[obj_cnt if obj_cnt < 2 else 2]
        return objects, context, obj_cnt

    def callback(self, body, **_):
        method = getattr(self, body["intents"]["intent"]["name"], self.default)
        pprint("----- METHOD CALLED -----")
        objects, context, obj_cnt = method(body)

        if objects != None and context != None:
            response = self.generate_text(objects, context, obj_cnt)
        else:
            response = "I didn't understand the question, could you repeat please."

        body["response"] = response
        body["path_done"].append(self.__class__.__name__)

        self.queue_manager.publish("ExternalInterface", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_generator = NaturalLanguageGenerator()
    natural_language_generator.run()


if __name__ == "__main__":
    main()
