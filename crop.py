import os
from common import Image, Tag, step_list, load_dataset_json
from status import get_step_images
from category import mesh_image_list
import json
from PIL import Image as pImage

# global list of warnings
warn = []

def crop_info():
	global warn
	warn = []

	data = load_dataset_json()
	if not data:
		data = {
			"crop" : {
				"warn" : ["No active dataset"]
			}
		}
		return data

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

	disk = get_step_images(step_list[1])
	
	images, missing = mesh_image_list(data["crop"], get_step_images(step_list[0]))
	
	data["crop"]["disk"] = []
	for i in disk: # also list output images [on disk]
		data["crop"]["disk"].append(i.get_id())

	nrm = [] # normalize values / remove useless keys
	for i in images:
		n = {}
		n["filename"] = i["filename"]

		if "crop_data" in i.keys():
			n["status"] = "auto" if i.get("auto") else "crop"
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
		
		if "duplicate" in i.keys():
			n["duplicate"] = i["duplicate"]

		nrm.append(n)
	images = nrm

	# find missing
	disk_only = list(set(data["crop"]["disk"]) - set([x["filename"] if "crop_data" in x.keys() else None for x in images]))
	if len(disk_only) > 0:
		warn.append(f"you have {len(disk_only)} image(s) that were cropped externally.")

	if data["crop"]["current"] > len(images):
		data["crop"]["current"] = 0
	data["crop"]["images"] = sorted(images, key=lambda x: x["filename"])
	data["crop"]["missing"] = missing
	data["crop"]["warn"] = warn
	return data

def crop_image(data, history):
	print("C:", data["filename"])
	if "ignored" in data.keys() and data["ignored"]:
		return
	if "crop_data" not in data.keys():
		return
	
	filename = data["filename"]
	old_path = os.path.join("0 - raw",filename)
	if filename in history:
		# if not data["duplicate"]: # doesn't work - sort order not preserved
			# print("file not a duplicate, but has duplicates?")
		path, ext = os.path.splitext(data["filename"])
		n = history.count(filename) + 1
		new_path = os.path.join("1 - cropped",f"{path}_{n}{ext}")
	else:
		new_path = os.path.join("1 - cropped",filename)

	if not os.path.isfile(old_path):
		warn.append(f"missing {old_path}")
		print(warn[-1])
		return
	if os.path.split(filename)[0]:
		cat = os.path.split(new_path)[0]
		if not os.path.isdir(cat):
			os.mkdir(cat)
	if os.path.isfile(new_path):
		print(f"already exists {new_path}")
		return filename
	crop = data["crop_data"]
	left = crop["x"]
	top = crop["y"]
	right = crop["x"]+crop["width"]
	bottom = crop["y"]+crop["height"]
	img = pImage.open(old_path)
	img = img.crop((left, top, right, bottom))
	img.save(new_path)
	return filename
