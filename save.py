import json

def save_json(new):
	"""Load current dataset.json and replace relevant sections"""
	print("Updating dataset.json")
	with open("dataset.json") as f:
		data = json.load(f)

	if "meta" in new.keys():
		print(" meta")
		data["meta"] = new["meta"]

	if "tags" in new.keys():
		print(" tags")
		data["tags"] = new["tags"]

	if "crop" in new.keys():
		print(" tags")
		data["crop"] = new["crop"]

	for key in new.keys():
		if key not in data.keys():
			print(f" add '{key}'")
			data[key] = new[key]

	with open("dataset.json", "w") as f:
		strdata = json.dumps(data, indent=2)
		f.write(strdata)