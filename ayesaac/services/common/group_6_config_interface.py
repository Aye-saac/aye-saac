import json

def recurs_find_val(obj, key):
	if key in obj:
		val = obj[key]
		return val
	for val in obj.values():
		if isinstance(val, dict):
			item = recurs_find_val(val, key)
			if item is not None:
				return item

# TODO: FIX NEEDED, NOT WORKING AS INTENDED
def recurs_append_val(obj, key, val):
	if key in obj:
		if isinstance(obj[key], list):
			obj[key].append(val)
			return obj
	for k, v in obj.items():
		if isinstance(v, dict):
			obj = recurs_append_val(obj, k, val)
			if obj is not None:
				print(obj)
				return obj


def get_config(path = "./group-6-config.json"):
	with open(path) as f:
		data = json.load(f)
		return data

def get_keys(path = "./group-6-config.json"):
	with open(path) as f:
		data = json.load(f)
		return data.keys()

def get_value(key, path = "./group-6-config.json", recursive = True):
	with open(path) as f:
		data = json.load(f)
		if recursive:
			val = recurs_find_val(data, key)
			return val
		else:
			return data[key]

def set_value(key, val, path = "./group-6-config.json"):
	with open(path, "r") as f:
		data = json.load(f)
	data[key] = val
	with open(path, "w") as f:
		json.dump(data, f)

def append_value(key, val, path = "./group-6-config.json", recursive = True):
	with open(path, "r") as f:
		data = json.load(f)
	if not recursive:
		data[key].append(val)
	else:
		data = recurs_append_val(data, key, val)
	with open(path, "w") as f:
		json.dump(data, f)
