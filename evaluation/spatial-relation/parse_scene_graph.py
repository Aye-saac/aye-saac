import json
import os
import shutil
import zipfile
import pickle
from pprint import pprint


# Get the GQA data first
if not (os.path.exists(os.path.join("GQA", "sceneGraphs", "train_sceneGraphs.json")) and os.path.exists(os.path.join("GQA", "images.zip")) and os.path.exists(os.path.join("GQA", "questions1.2", "train_balanced_questions.json"))):
    print("Data missing! Download the GQA data from https://cs.stanford.edu/people/dorarad/gqa/download.html and place in a directory called GQA. Extract the questions1.2.zip and sceneGraphs.zip files and then re-run this script. You do not need to extract the images.zip file.")
    exit(0)

if not os.path.exists(os.path.join("GQA", "kitchen_images")):
    os.mkdir(os.path.join("GQA", "kitchen_images"))

#######################################################
# GQA images
print("Getting kitchen-specific images")
path = os.path.join("GQA", "sceneGraphs", "train_sceneGraphs.json")
with open(path, "r") as json_file:
    data = json.load(json_file)

kitchen_images = []
for image_id in data:
    if "objects" in data[image_id]:
        for obj in data[image_id]["objects"].values():
            if "kitchen" in obj["name"]:
                kitchen_images.append(image_id)
                break
print("Found {k} kitchen-specific images".format(k=len(kitchen_images)))

# extract only these images
zip_path = os.path.join("GQA", "images.zip")
target_dir = os.path.join("GQA", "kitchen_images")

print("Extracting kitchen-specific images to {t}".format(t=target_dir))
with zipfile.ZipFile(zip_path) as z:
    for image in kitchen_images:
        with z.open("images/{i}.jpg".format(i=image)) as zf, open(os.path.join(target_dir, os.path.basename("{i}.jpg".format(i=image))), 'wb') as f:
            shutil.copyfileobj(zf, f)

#######################################################
# GQA questions
print("Getting questions for kitchen-specific images")
path = os.path.join("GQA", "questions1.2", "train_balanced_questions.json")
with open(path, "r") as json_file:
    data = json.load(json_file)

positions = []
for question in data:
    if data[question]["imageId"] in kitchen_images:
        positions.append({
            "questionId": question,
            "imageId": data[question]["imageId"],
            "question": data[question]["question"],
            "fullAnswer": data[question]["fullAnswer"],
            "semanticType": data[question]["types"]["semantic"],
            "structuralType": data[question]["types"]["structural"]
        })

print("Outputting to gqa_positions.tsv and positions.pickle")
positions.sort(key=lambda x: x["imageId"])
with open('gqa_positions.tsv', 'w') as out:
    out.write(
            "{id}\t{q}\t{a}\t{s}\t{t}\n".format(
                id="imageId",
                q="question",
                a="fullAnswer",
                s="semanticType",
                t="structuralType"
            )
    )
    for position in positions:
        out.write(
            "{id}\t{q}\t{a}\t{s}\t{t}\n".format(
                id=position["imageId"],
                q=position["question"],
                a=position["fullAnswer"],
                s=position["semanticType"],
                t=position["structuralType"]
            )
        )

# write the data with pickle
with open("positions.pickle", "wb") as f:
    pickle.dump(positions, f)

print("Finished - now manually remove any grayscale images from {t} before running next script: eval_spatial_relations.py".format(t=target_dir))