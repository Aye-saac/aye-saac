from ayesaac.services.common import QueueManager
from ayesaac.utils.logger import get_logger
import re
import json

logger = get_logger(__file__)

class LabelFormatter(object):
    def __init__(self):
        self.queue_manager = QueueManager([self.__class__.__name__, "Interpreter"])

    def callback(self, body, **_):
        patterns = []
        with open("./group-6-config.json") as f:
            data = json.load(f)
            patterns = data["label-keywords"]

        text = " ".join(" ".join(t) for t in body["texts"])
        logger.info(text)
        logger.info(body["texts"])
        text = re.sub('\s+\n', ' ', text).lower()
        text = re.sub('[^a-z0-9(),%*. ]+', '', text)
        text = [text]
        regex = '(^.*'
        regex += "|".join(pattern for pattern in patterns)
        regex += ')'
        text = re.split(regex, text[0])
        data = {}
        print(text)
        max_len = -1
        likely_string = None
        for pattern in patterns:
            likely_string = ""
            for i in range(len(text)):
                if (text[i] != ''):
                    if (text[i] == pattern):
                        next_string = text[i+1]
                        cur_len = len(next_string)

                        # Assume that the longest string after pattern is the one
                        if (cur_len > max_len):
                            max_len = cur_len
                            likely_string = next_string
                    data[pattern] = likely_string

        body["extracted_label"] = data

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
