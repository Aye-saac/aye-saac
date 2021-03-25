from ayesaac.services.common import QueueManager
from ayesaac.utils.logger import get_logger
import re
import json

from ayesaac.services.common.group_6_config_interface import get_value

logger = get_logger(__file__)

class LabelFormatter(object):
    def split_by_keywords(self, text, keywords):
        text = [text]
        regex = '(^.*'
        regex += "|".join(keyword for keyword in keywords)
        regex += ')'
        text = re.split(regex, text[0])
        data = {}
        max_len = -1
        likely_string = None
        for keyword in keywords:
            likely_string = ""
            for i in range(len(text)):
                if (text[i] != ''):
                    if (text[i] == keyword):
                        next_string = text[i+1]
                        cur_len = len(next_string)

                        # Assume that the longest string after pattern is the one
                        if (cur_len > max_len):
                            max_len = cur_len
                            likely_string = next_string

                    data[keyword] = likely_string
        return data

    def find_category(self, text, category):
        matches = []
        for item in category:
            match = re.search(item, text)
            if (match != None):
                matches.append(item)
                print(matches)
        return matches


    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

    def callback(self, body, **_):
        # Normalize texts array into a string
        text = " ".join(" ".join(t) for t in body["texts"])

        # Replace all whitespaces by single space
        text = re.sub('\s+\n', ' ', text).lower()

        # Keep only alphanumerics, parentheses, commas, asterisks, and percent signs
        text = re.sub('[^a-z0-9(),%*. ]+', '', text)

        # Get keywords to look for from config file
        keywords = get_value("label-keywords")

        # Split label text by keyword and return as json
        body["extracted_label"] = self.split_by_keywords(text, keywords)

        dairy = ["dairy", "milk", "butter", "cream", "cheese", "yogurt"]
        nuts = ["nuts", "peanuts", "pecans", "walnuts", "almonds", "brazil nuts", "cashews",
            "chesnuts", "filberts", "hazelnuts", "macadamia", "pine nuts", "pistachios"]
        meat = ["meat", "chicken", "pork", "beef", "veal"]
        allergens = ["celery", "gluten", "crustaceans", "eggs", "fish", "lupin", "milk",
            "molluscs", "mustard", "peanuts", "sesame", "soybeans", "sulphur dioxide",
            "sulphites", "tree nuts"]
        ingredient_testing = ["milk", "water", "flour", "potato"]

        body["extracted_label"]["allergens"] = self.find_category(text, allergens)
        body["extracted_label"]["nuts"]      = self.find_category(text, nuts)
        body["extracted_label"]["meat"]      = self.find_category(text, meat)
        body["extracted_label"]["dairy"]     = self.find_category(text, dairy)

        next_service = body["vision_path"].pop(0)
        self.queue_manager.publish(next_service, body)

        logger.info(f"{self.__class__.__name__} ready")

    def run(self):
        self.queue_manager.start_consuming(self.__class__.__name__, self.callback)

def main():
    lf = LabelFormatter()
    lf.run()


if __name__ == "__main__":
    main()
