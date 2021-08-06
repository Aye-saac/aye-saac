from ayesaac.utils.config import Config

# Get the EPIC-KITCHENS label file
config = Config()
label_file = open(config.directory.data.joinpath("epic_kitchens").joinpath("EPICKitchens_FasterRCNN_label_map.pbtxt"), 'r')
lines = label_file.readlines()

# Read the EPIC-KITCHENS categories from the label file into a dictionary
epic_kitchens_category_index = {}
item_id = None
for line in lines:
    line = line.strip()
    
    if line.startswith("id:"):
        item_id = line.split(" ")[1]
    
    if line.startswith("name:"):
        item_name = line.split(" ")[1]
        item_name = item_name.replace("'", "")
        epic_kitchens_category_index[int(item_id)] = {"id": int(item_id), "name": item_name}