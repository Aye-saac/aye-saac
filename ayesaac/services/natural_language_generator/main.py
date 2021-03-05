import os
from pprint import pprint
from random import choice

from ayesaac.services.common import QueueManager
from ayesaac.utils.config import Config
from ayesaac.utils.logger import get_logger


config = Config()


logger = get_logger(__file__)


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
        if (word[1] > 1):
            return str(word[1]) + " "
        elif word[1] == 1:
            return "a "
        else:
            return "no "

    def compare_name_value(self, name, value):
        if name == value:
            return True
        elif name == value[:-1] and value[-1] == 's':
            return True
        return False

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
                self.get_det(words[0]) + words[0][0],
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
                if self.compare_name_value(o["name"], p["value"]):
                    objects.append(
                        p["value"]
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
        print(objects)
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
                if self.compare_name_value(o["name"], p["value"]):
                    objects = (p["value"], o["colour"])
                    break
                else:
                    objects = (p["value"], None)
        if objects:
            obj_cnt = 1 if objects[1] else 0
            objects = objects[obj_cnt]
            context = "COLOR_DETECTION" if obj_cnt else "COLOR_DETECTION_N"
        return objects, context, obj_cnt

    def count(self, body):
        pprint("count")
        obj_cnt = 0
        objects = []
        context = ""

        for o in body["objects"]:
            for p in body["intents"]["entities"]:
                if self.compare_name_value(o["name"], p["value"]):
                    objects.append(p["value"])
        objects = list(set([(o, objects.count(o)) for o in objects]))
        obj_cnt = sum(n for _, n in objects)
        for p in body["intents"]["entities"]:
            elements = [x for x in objects if x[0] == p["value"]]
            if not len(elements):
                objects.append((p["value"], 0))
        context = "DESCRIPTION_COUNT"
        return objects, context, obj_cnt

    def locate(self, body):
        pprint("locate")

        objects = []
        for o in body["objects"]:
            for p in body["intents"]["entities"]:
                if self.compare_name_value(o["name"], p["value"]):
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
                        p["value"]
                        + (o["lateral_position"] if o.get("lateral_position") else "")
                    )
        objects = list(set([(o, objects.count(o)) for o in objects]))
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
        pprint(body)

        method = getattr(self, body["intents"]["intent"]["name"], self.default)
        pprint("----- METHOD CALLED -----")
        objects, context, obj_cnt = method(body)

        print(objects)
        print(context)

        if objects != None and context != None:
            response = self.generate_text(objects, context, obj_cnt)
        else:
            response = "I didn't understand the question, could you repeat please."

        body["response"] = response
        pprint(body["response"])
        body["path_done"].append(self.__class__.__name__)

        self.queue_manager.publish("ExternalInterface", body)

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)


def main():
    natural_language_generator = NaturalLanguageGenerator()
    natural_language_generator.run()


if __name__ == "__main__":
    main()
