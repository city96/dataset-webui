import os
from common import Image, Tag, step_list
from status import get_step_images
import json
from PIL import Image as pImage

# global list of warnings
warn = []

def crop_info():
	global warn
	warn = []
	if not os.path.isfile("dataset.json"):
		data = {
			"crop" : {
				"warn" : ["No images"]
			}
		}
		return data
	
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
	if "disk" not in data["crop"].keys():
		data["crop"]["disk"] = []

	data = { # filter extra data
		"crop" : data["crop"]
	}

	images = []
	missing = []
	valid = get_step_images(step_list[0])
	disk = get_step_images(step_list[1])

	for i in data["crop"]["images"]:
		if i["filename"] in [x.get_id() for x in valid]:
			images.append(i)
		else:
			missing.append(i)

	for i in data["crop"]["missing"]:
		if i["filename"] in [x.get_id() for x in valid]:
			images.append(i)
		else:
			missing.append(i)
	
	for i in disk: # also list output images [on disk]
		data["crop"]["disk"].append(i.get_id())

	for i in valid:
		if i.get_id() in [x["filename"] for x in images]:
			continue
		if i.get_id() in [x["filename"] for x in missing]:
			continue
		images.append({
			"filename" : i.get_id(),
			"category" : i.category,
		})

	nrm = [] # normalize values / remove useless keys
	for i in images:
		n = {}
		n["filename"] = i["filename"]

		if "crop_data" in i.keys():
			n["status"] = "crop"
			n["crop_data"] = i["crop_data"]
		else:
			n["status"] = "raw"

		if "ignored" in i.keys():
			n["ignored"] = i["ignored"]
			if i["ignored"]:
				n["status"] = "ignored"
		
		if i["filename"] in data["crop"]["disk"]:
			n["on_disk"] = True
		else:
			n["on_disk"] = False

		nrm.append(n)
	images = nrm

	# find missing
	disk_only = list(set(data["crop"]["disk"]) - set([x["filename"] if "crop_data" in x.keys() else None for x in images]))
	if len(disk_only) > 0:
		warn.append(f"you have {len(disk_only)} image(s) that were cropped externally.")

	if data["crop"]["current"] > len(images):
		data["crop"]["current"] = 0
	data["crop"]["images"] = images
	data["crop"]["missing"] = missing
	data["crop"]["warn"] = warn
	return data

def crop_image(data):
	old_path = os.path.join("0 - raw",data["filename"])
	new_path = os.path.join("1 - cropped",data["filename"])
	if not os.path.isfile(old_path):
		warn.append(f"missing {old_path}")
		print(warn[-1])
		return
	if os.path.split(data["filename"])[0]:
		cat = os.path.split(new_path)[0]
		if not os.path.isdir(cat):
			os.mkdir(cat)
	if os.path.isfile(new_path):
		print(f"already exists {new_path}")
		return
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
		if i["filename"] in [x.get_id() for x in valid]:
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