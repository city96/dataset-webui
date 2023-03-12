import json

def save_json(new):
	"""Load current dataset.json and replace relevant sections"""
	print("Updating dataset.json")
	with open("dataset.json") as f:
		data = json.load(f)

	if "meta" in new.keys():
		print(" meta")
		data["meta"] = new["meta"]

	if "crop" in new.keys():
		print(" crop")
		new["crop"].pop('disk', None)
		new["crop"].pop('warn', None)
		data["crop"] = new["crop"]

	if "sort" in new.keys():
		print(" sort")
		if "sort" not in data.keys():
			data["sort"] = {}
		if "categories" in new["sort"].keys():
			print("  cat")
			data["sort"]["categories"] = new["sort"]["categories"]
		if "images" in new["sort"].keys():
			print("  img")
			data["sort"]["images"] = new["sort"]["images"]

	if "tags" in new.keys():
		print(" tags")
		data["tags"] = new["tags"]

	for key in new.keys():
		if key not in data.keys():
			print(f" add '{key}'")
			data[key] = new[key]

	with open("dataset.json", "w") as f:
		strdata = json.dumps(data, indent=2)
		f.write(strdata)