import json
from common import load_dataset_json, version

def save_json(new):
	"""Load current dataset.json and replace relevant sections"""
	print("Updating dataset.json")
	data = load_dataset_json()

	if "meta" in new.keys() and new["meta"]:
		print(" meta")
		data["meta"] = new["meta"]

	if "crop" in new.keys() and new["crop"]:
		print(" crop")
		new["crop"].pop('disk', None)
		new["crop"].pop('warn', None)
		data["crop"] = new["crop"]

	if "sort" in new.keys() and new["sort"]:
		print(" sort")
		if "sort" not in data.keys():
			data["sort"] = {}
		if "categories" in new["sort"].keys() and new["sort"]["categories"]:
			print("  cat")
			data["sort"]["categories"] = new["sort"]["categories"]
		if "images" in new["sort"].keys() and new["sort"]["images"]:
			print("  img")
			data["sort"]["images"] = new["sort"]["images"]

	if "tags" in new.keys() and new["tags"]:
		print(" tags")
		if "tags" not in data.keys():
			data["tags"] = {}
		if "rules" in new["tags"].keys() and new["tags"]["rules"]:
			print("  rules")
			data["tags"]["rules"] = new["tags"]["rules"]
		if "images" in new["tags"].keys() and new["tags"]["images"]:
			print("  img")
			data["tags"]["images"] = new["tags"]["images"]
			if "missing" in new["tags"].keys():
				data["tags"]["missing"] = new["tags"]["missing"]

	for key in new.keys():
		if key not in data.keys():
			print(f" add '{key}'")
			data[key] = new[key]

	data["meta"]["version"] = version # upgrade

	with open("dataset.json", "w") as f:
		strdata = json.dumps(data, indent=2)
		f.write(strdata)