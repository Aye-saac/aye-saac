import unicodedata
import re
import json

def extract_label(text):
    patterns = []
    with open("./group-6-config.json") as f:
        data = json.load(f)
        patterns = data["label-keywords"]

    # text = unicodedata.normalize('NFKD', udata)
    text = re.sub('\s+', ' ', text).lower()
    text = re.sub('[^a-z0-9 ]+', '', text)
    text = [text]

    data = {}

    max_len = -1
    likely_string = None
    for pattern in patterns:
        likely_string = ""
        for element in text:
            split = re.split('('+pattern+')', element)

            for i in range(len(split)):
                if (split[i] == pattern):
                    next_string = split[i+1]
                    cur_len = len(next_string)

                    if (cur_len > max_len):
                        max_len = cur_len
                        likely_string = next_string
        data[pattern] = likely_string
        # data.append(json.loads('{ "' + pattern + '": "' + likely_string + '" }'))

    # json_string = '{' + json.dumps(data)[1:-1] + '}'
    # json_data = json.loads(json_string)
    # return json_data
    return json.dumps(data)
