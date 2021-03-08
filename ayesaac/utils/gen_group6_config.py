import json
import os

data = {}

data["default-ocr-model"] = "tesseract"

data["supported-ocr-models"] = [
    "keras-ocr",
    "tesseract"
]

data["label-keywords"] = [
    "ingredients",
    "allergens"
]

'''
Since the path of cwd and of actual script can be different, you will have to
move the json file to the aye-saac root directory IF you need to run this.
If anyone has an elegant solution let me know
'''
with open("group-6-config.json", "w+") as f:
    json_string = json.dumps(data)
    f.write(json_string)
