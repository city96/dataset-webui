import json

def save_json(new):
	"""Load current dataset.json and replace relevant sections"""
	print("Updating dataset.json")
	with open("dataset.json") as f:
		data = json.load(f)

	if "meta" in new.keys() and new["meta"]:
		print(" meta")
		data["meta"] = new["meta"]

	if "crop" in new.keys() and new["new"]:
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
		data["tags"] = new["tags"]

	for key in new.keys():
		if key not in data.keys():
			print(f" add '{key}'")
			data[key] = new[key]

	with open("dataset.json", "w") as f:
		strdata = json.dumps(data, indent=2)
		f.write(strdata)