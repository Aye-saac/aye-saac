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
        synonyms_regex = []
        for keyword in keywords:
          synonyms_regex.append("|".join(synonym for synonym in keywords[keyword]))

        regex += "|".join(synonym_regex for synonym_regex in synonyms_regex)
        regex += ')'
        text = re.split(regex, text[0])
        data = {}
        max_len = -1
        likely_string = None
        for keyword in keywords:
            likely_string = ""
            for i in range(len(text)):
                if (text[i] != ''):
                    if (text[i] in keywords[keyword]):
                        next_string = text[i+1]
                        cur_len = len(next_string)

                        # Assume that the longest string after pattern is the one
                        if (cur_len > max_len):
                            max_len = cur_len
                            likely_string = next_string

                    data[keyword] = likely_string
        return data

    def find_category(self, text, cat_name, cat_elems):
        matches = []
        for item in cat_elems:
            match = re.search(item, text)
            if (match != None):
                matches.append(item)

        if (len(matches) > 0):
            logger.info("Found matches: " + str(matches) + " for " + cat_name)
        return matches


    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

    def callback(self, body, **_):
        # Normalize texts array into a string
        text = " ".join(" ".join(t) for t in body["texts"])

        # Replace all whitespaces by single space
        # Keep only alphanumerics, parentheses, commas, asterisks, and percent signs
        text = re.sub('\s+\n', ' ', text).lower()
        text = re.sub('[^a-z0-9(),%*. ]+', '', text)

        # Get keywords to look for from config file
        keywords = get_value("label-keywords")

        # Split label text by keyword and return as json
        body["extracted_label"] = self.split_by_keywords(text, keywords)
        categories = get_value("categories")
        # logger.info(categories)
        for category in categories.keys():
            body["extracted_label"][category] = self.find_category(text, category, categories[category])

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
