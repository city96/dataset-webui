import os
from common import Image, Tag, step_list
from status import get_step_images
import json

def crop_info():
	with open("dataset.json") as f:
		data = json.load(f)

	if "crop" not in data.keys():
		data["crop"] = {}
	if "images" not in data["crop"].keys():
		data["crop"]["images"] = []
	if "missing" not in data["crop"].keys():
		data["crop"]["missing"] = []
	if "current" not in data["crop"].keys():
		data["crop"]["current"] = 0

	images = []
	missing = []
	valid = get_step_images(step_list[0])
	for i in data["crop"]["images"]:
		if i["filename"] in [x.filename for x in valid]:
			images.append(i)
		else:
			missing.append(i)
	for i in data["crop"]["missing"]:
		if i["filename"] in [x.filename for x in valid]:
			images.append(i)
		else:
			missing.append(i)
	for i in valid:
		if i.filename in [x["filename"] for x in images]:
			continue
		if i.filename in [x["filename"] for x in missing]:
			continue
		images.append({
			"filename" : i.filename,
			"status" : "raw",
			"size" : None,
			"date" : None,
		})
	data["crop"]["images"] = images
	data["crop"]["missing"] = missing
	return data

# print(json.dumps(crop_info(), indent=2))