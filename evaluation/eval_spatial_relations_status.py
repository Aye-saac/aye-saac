import requests
import pickle
import shutil
import os


# Check the data is ready
if not os.path.exists("responses.pickle"):
    print("Run eval_spatial_relations.py first")
    exit(0)
    
file_dir = "//wsl$/docker-desktop-data/version-pack-data/community/docker/volumes/aye-saac_output_data/_data/"
if not os.path.exists(file_dir):
    print("The Docker output directory doesn't exist - update the path manually")
    exit(0)

print("Parsing responses.pickle")
data = []
with (open("responses.pickle", "rb")) as f:
    while True:
        try:
            data = pickle.load(f)
        except EOFError:
            break

print("Sending GET requests and moving files")
for d in data:
    url = "http://localhost:5000{s}".format(s=d["status"])
    response = requests.request("GET", url)
    if response.status_code == 200:
        print("{f}: {r}".format(f=d["file"], r=response.json()["response"]))
        d["ayesaac_answer"] = response.json()["response"]
        path = os.path.join("SpatialRelations", d["file"])
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        
        try:
            shutil.copy(
                "{f}{u}.txt".format(
                    f=file_dir,
                    u=d["uid"]
                ),
                os.path.join(path, "{f}.txt".format(f=d["file"]))
            )
        except FileNotFoundError:
            pass
        try:
            shutil.copy(
                "{f}bbox.{u}.png".format(
                    f=file_dir,
                    u=d["uid"]
                ),
                os.path.join(path, "{f}.bbox.png".format(f=d["file"]))
            )
        except FileNotFoundError:
            pass
        try:
            shutil.copy(
                "{f}bbox_filtered.{u}.png".format(
                    f=file_dir,
                    u=d["uid"]
                ),
                os.path.join(path, "{f}.bbox_filtered.png".format(f=d["file"]))
            )
        except FileNotFoundError:
            pass
    else:
        print("{f}: Issue!: {r}".format(f=d["file"], r=response.status_code))

print("Outputting to spatial_reasoning_results.tsv")
with open('spatial_reasoning_results.tsv', 'w') as out:
        out.write(
             "{id}\t{qid}\t{q}\t{g}\t{a}\n".format(
                    id="imageId",
                    qid="questionId",
                    q="question",
                    g="gqa_answer",
                    a="ayesaac_answer"
                )
        )
        for d in data:
            out.write(
                "{id}\t{qid}\t{q}\t{g}\t{a}\n".format(
                    id=d["file"],
                    qid=d["questionId"],
                    q=d["message"],
                    g=d["gqa_answer"],
                    a=d["ayesaac_answer"]
                )
            )

print("Finished")