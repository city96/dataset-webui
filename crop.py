import os
from common import Image, Tag, step_list
from status import get_step_images
import json
from PIL import Image as pImage

# global list of warnings
warn = []

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

def crop_image(data):
	old_path = os.path.join("0 - raw",data["filename"])
	new_path = os.path.join("1 - cropped",data["filename"])
	if not os.path.isfile(old_path):
		warn.append(f"missing {old_path}")
		print(warn[-1])
		return
	if os.path.isfile(new_path):
		pass # just overwrite for now
		# print(f"already exists {new_path}")
		# return
	crop = data["crop_data"]
	left = crop["x"]
	top = crop["y"]
	right = crop["x"]+crop["width"]
	bottom = crop["y"]+crop["height"]
	img = pImage.open(old_path)
	img = img.crop((left, top, right, bottom))
	img.save(new_path)


def apply_crop():
	global warn
	warn = []
	with open("dataset.json") as f:
		data = json.load(f)
	if "crop" not in data.keys() or "images" not in data["crop"].keys():
		return

	valid = get_step_images(step_list[0])
	cropped = 0
	for i in data["crop"]["images"]:
		if i["filename"] in [x.filename for x in valid]:
			if "ignored" in i.keys() and i["ignored"]:
				continue
			if "crop_data" not in i.keys():
				continue
			print("CROPPING", i)
			crop_image(i)
			cropped += 1
	if not warn:
		warn = [f"cropped {cropped} images"]
	return warn