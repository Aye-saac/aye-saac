import json

def get_config(path = "./group-6-config.json"):
	with open(path) as f:
		data = json.load(f)
		return data

def get_keys(path = "./group-6-config.json"):
	with open(path) as f:
		data = json.load(f)
		return data.keys()

def get_value(key, path = "./group-6-config.json"):
	with open(path) as f:
		data = json.load(f)
		return data[key]

def set_value(key, val, path = "./group-6-config.json"):
	with open(path) as f:
		data = json.load(f)
		data[key] = val
