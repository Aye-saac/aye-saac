import csv

from ayesaac.utils.config import Config

# Get the EPIC-KITCHENS CSV file
config = Config()
csv_file = config.directory.data.joinpath("epic_kitchens").joinpath("EPIC_noun_classes.csv")

# Read the EPIC-KITCHENS categories from the CSV file into a dictionary
epic_kitchens_category_index = {}
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile)
    next(reader) # skip header
    for rows in reader:
        id = int(rows[0])
        name = rows[1]
        epic_kitchens_category_index[id] = {"id": id, "name": name}
