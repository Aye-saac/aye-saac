import requests
import pickle
from pprint import pprint
import time
import os


# Check the data is ready
if not os.path.exists("positions.pickle"):
    print("Run parse_scene_graph.py first")
    exit(0)

directory = os.path.join("GQA", "kitchen_images")
if not os.path.exists(directory):
    os.mkdir(directory)
    
url = "http://localhost:5000/submit"

print("Parsing positions.pickle")
data = []
positions = []
with (open("positions.pickle", "rb")) as f:
    while True:
        try:
            positions = pickle.load(f)
        except EOFError:
            break 

for position in positions:
    # take where questions only,
    if position["question"].lower().startswith("where") and position["semanticType"] == "rel":
        if os.path.isfile("{d}/{f}.jpg".format(d=directory, f=position["imageId"])):
            data.append({
                "questionId": position["questionId"],
                "message": position["question"],
                "file": position["imageId"],
                "status": "",
                "uid": "",
                "gqa_answer": position["fullAnswer"]
            })

print("Sending POST requests")
count = 1
for d in data:
    payload = {"message": d["message"]}
    files = [
        (
            "image",
            (
                "{f}.jpg".format(f=d["file"]),
                open("{d}/{f}.jpg".format(d=directory, f=d["file"]), "rb"),
                "image/jpeg",
            ),
        )
    ]
    response = requests.request("POST", url, data=payload, files=files)
    d["status"] = response.text
    d["uid"] = response.text.replace("/status/", "")
    print(str(count) + ": " + str(d))
    time.sleep(5)
    count += 1

print("Outputting to responses.pickle")
# write the data with pickle
with open("responses.pickle", "wb") as f:
    pickle.dump(data, f)

print("Finished - now run next script: eval_spatial_relations_status.py")