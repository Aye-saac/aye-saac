import shutil, json, os
import pandas as pd

# Run the download_eval_data.sh script first
if not (os.path.exists("Images") and os.path.exists("Annotations")):
    print("Run the download_eval_data.sh script first")
    exit(0)

# read in the list of files of interest, these were selected using the VizWiz browser
# using the following criteria: OBJ (object detection), NONE (no quality issues) and
# keyword search within captions for "kitchen"
with open('./images_of_interest.txt') as f:
    images = f.read().splitlines()

# move the images to a directory
for img in images:
    shutil.copy(f'./Images/{img}', f'./SelectedImages/{img}')

# read in the val and train jsons
with open('./Annotations/val.json') as f:
    val = json.load(f)
    
with open('./Annotations/train.json', encoding="utf8") as f:
    train = json.load(f)

# get the relevant json data for the images of interest
val_of_interest = [v for v in val if v['image'] in images]
train_of_interest = [t for t in train if t['image'] in images]

# combine the lists and print to file
data_of_interest = val_of_interest + train_of_interest
with open('data_of_interest.json', 'w') as out:
    json.dump(data_of_interest, out)

# save the data to a pandas dataframe for outputting to csv
df = pd.DataFrame(data_of_interest)

# get the confidence scores by summing the number that have answer_confidence=yes
def calc_confidence(row):
    sum = 0
    for answer in row[2]:
        if answer['answer_confidence'] == 'yes':
            sum += 1
    row['sum_confidence'] = sum
    return row

df = df.apply(calc_confidence, axis=1)
print("Number of images with 1-10 confidence (number of correct answers)")
print(df['sum_confidence'].value_counts())

# output to file
df.to_csv("data_of_interest.tsv", sep="\t", index=False)

